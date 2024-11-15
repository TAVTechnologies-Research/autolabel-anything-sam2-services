import os
import io
import time
import glob
import base64

from typing import Union, Optional, List, Tuple, Generator

import torch
import cv2 as cv
import numpy as np
from PIL import Image
from tqdm import tqdm

from schemas import Point, PointPrompt
from sam2.build_sam import build_sam2_video_predictor
from sam2.sam2_video_predictor import SAM2VideoPredictor


class SegmentAnything2:
    def __init__(
        self,
        model_path: str,
        model_config: str,
        device: Union[torch.device, str] = "cuda",
    ) -> None:
        """
        Params probably passed via a database table
        :param model_path: path to the model .pth file
        :param model_config: path to the model config .yaml file
        """
        self.model_path = model_path
        self.model_config = model_config
        self.device = torch.device(device)

        if self.device.type == "cuda":
            with torch.autocast("cuda", dtype=torch.bfloat16):
                if torch.cuda.get_device_properties(0).major >= 8:
                    torch.backends.cuda.matmul.allow_tf32 = True
                    torch.backends.cudnn.allow_tf32 = True

        # ----- default settings ----- #
        self.offload_video_to_cpu: bool = True
        self.async_loading_frames: bool = False

        self.predictor = build_sam2_video_predictor(
            config_file=self.model_config,
            ckpt_path=self.model_path,
            device=self.device.type,
            mode="eval",
            apply_postprocessing=True,
        )

        self._inference_state: Optional[dict] = None

    def reset_state(self) -> None:
        if self.inference_state is not None:
            self.predictor.reset_state(self.inference_state)

    @property
    def inference_state(self) -> dict:
        if self._inference_state is not None:
            return self._inference_state
        else:
            raise ValueError("Inference state not initialized")

    @inference_state.setter
    def inference_state(self, state: dict):
        self._inference_state = state

    # FIXME: Find a way to avoid loading the frames into memory
    def init_state(self, video_dir: str) -> Optional[dict]:
        """Initialize the SAM2 model which includes
        loading the frames into the memory.

        Args:
            video_dir (str): frames directory

        Returns:
            dict: state of the model
        """
        try:
            self.inference_state = self.predictor.init_state(video_dir)
            self.predictor.reset_state(self.inference_state)

        except Exception as e:
            raise ValueError(f"Error initializing model: {e}. Object ID: {id(self)}")

    def add_point_prompt(
        self,
        frame_idx: int,
        points: List[np.ndarray],
        labels: List[np.ndarray],
        object_ids: List[str | int],
    ) -> Tuple[int, List[Union[int, str]], np.ndarray]:
        """Add point prompt to the model state

        Args:
            point_prompt (PointPrompt): point prompt
        Returns:
            Tuple[List[Union[int, str]], np.ndarray]: object_ids and mask logits
            Mask logits are the shape of (N, 1, H, W) where N is the number of objects
        """
        for point, label, obj_id in zip(
            points, labels, object_ids
        ):  # remember: each object needs to added seperately on a frame
            with torch.autocast("cuda", dtype=torch.bfloat16):
                out_frame_idx, out_obj_ids, out_mask_logits = (
                    self.predictor.add_new_points_or_box(
                        inference_state=self.inference_state,
                        frame_idx=frame_idx,
                        points=point,
                        labels=label,
                        obj_id=obj_id,
                        clear_old_points=True,
                        normalize_coords=False,  # points expected to be normalized
                    )
                )
        return (
            out_frame_idx,
            out_obj_ids,
            np.squeeze(
                (out_mask_logits > 0)
                .permute(0, 2, 3, 1)
                .cpu()
                .numpy()
                .astype(np.int64),
                axis=-1,
            ),
        )

    def run_inference(
        self,
    ) -> Generator[Tuple[int, List[Union[int, str]], np.ndarray], None, None]:
        """Run inference on the model state

        Yields:
            Generator[Tuple[List[Union[int, str]], np.ndarray], None, None]: object_ids and mask logits
            Mask logits are the shape of (N, 1, H, W) where N is the number of objects
        """
        # FIXME: On the second run call the reset state method -> hold an attribute if reset state called after video propagation

        with torch.autocast("cuda", dtype=torch.bfloat16):
            for (
                out_frame_idx,
                out_obj_ids,
                out_mask_logits,
            ) in self.predictor.propagate_in_video(
                inference_state=self.inference_state
            ):
                yield out_frame_idx, out_obj_ids, np.squeeze(
                    (out_mask_logits > 0)
                    .permute(0, 2, 3, 1)
                    .cpu()
                    .numpy()
                    .astype(np.int64),
                    axis=-1,
                )
                
    def remove_object(self, object_id: Union[int, str]) -> None:
        """Remove object from the model state

        Args:
            object_id (Union[int, str]): object id
        """
        self.predictor.remove_object(inference_state=self.inference_state, obj_id=object_id, need_output=False)

    # TODO move non-model related methods under a cv module
    def mask_to_image(self, mask: np.ndarray) -> np.ndarray:
        """Convert mask to image

        Args:
            mask (np.ndarray): mask out [HxW]

        Returns:
            np.ndarray: mask image -> [HxWx3]
        """
        mask = mask.astype(np.uint8) * 255
        mask = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
        return mask

    def image_to_base64(self, src_image: np.ndarray) -> str:
        """Convert image to base64

        Args:
            image (np.ndarray): image

        Returns:
            str: base64 encoded image
        """
        image = Image.fromarray(src_image)
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
