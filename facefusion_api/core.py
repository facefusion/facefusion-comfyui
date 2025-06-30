from concurrent.futures import ThreadPoolExecutor
from functools import partial
from io import BytesIO
from typing import Tuple

import torch
from comfy.comfy_types import IO
from comfy_api.input_impl.video_types import VideoFromComponents
from comfy_api.util import VideoComponents
from comfy_api_nodes.apinode_utils import bytesio_to_image_tensor, tensor_to_bytesio
from httpx import Client as HttpClient, Headers
from torch import Tensor

from .types import FaceSwapperModel, InputTypes


class SwapFaceImage:
	@classmethod
	def INPUT_TYPES(s) -> InputTypes:
		return\
		{
			'required':
			{
				'source_image': (IO.IMAGE,),
				'target_image': (IO.IMAGE,),
				'api_token':
				(
					'STRING',
					{
						'default': '0'
					}
				),
				'face_swapper_model':
				(
					[
						'hyperswap_1a_256',
						'hyperswap_1b_256',
						'hyperswap_1c_256'
					],
					{
						'default': 'hyperswap_1c_256'
					}
				)
			}
		}

	RETURN_TYPES = (IO.IMAGE,)
	FUNCTION = 'process'
	CATEGORY = 'FaceFusion API'

	@staticmethod
	def process(source_image : Tensor, target_image : Tensor, api_token : str, face_swapper_model : FaceSwapperModel) -> Tuple[Tensor]:
		output_tensor: Tensor = SwapFaceImage.swap_face(source_image, target_image, api_token, face_swapper_model)
		return (output_tensor,)

	@staticmethod
	def swap_face(source_tensor : Tensor, target_tensor : Tensor, api_token : str, face_swapper_model : FaceSwapperModel) -> Tensor:
		source_buffer : BytesIO = tensor_to_bytesio(source_tensor, mime_type = 'image/webp')
		target_buffer : BytesIO = tensor_to_bytesio(target_tensor, mime_type = 'image/webp')

		url = 'https://api.facefusion.io/inferences/swap-face'
		files =\
		{
			'source': ('source.webp', source_buffer, 'image/webp'),
			'target': ('target.webp', target_buffer, 'image/webp'),
		}
		data =\
		{
			'face_swapper_model': face_swapper_model,
		}
		headers = Headers()

		if api_token:
			headers['X-Token'] = api_token

		with HttpClient(timeout = 10) as http_client:
			response = http_client.post(url, headers = headers, files = files, data = data)

		output_buffer = BytesIO(response.content)
		output_tensor = bytesio_to_image_tensor(output_buffer)
		return output_tensor


class SwapFaceVideo:
	@classmethod
	def INPUT_TYPES(s) -> InputTypes:
		return\
		{
			'required':
			{
				'source_image': (IO.IMAGE,),
				'target_video': (IO.VIDEO,),
				'api_token':
				(
					'STRING',
					{
						'default': '0'
					}
				),
				'face_swapper_model':
				(
					[
						'hyperswap_1a_256',
						'hyperswap_1b_256',
						'hyperswap_1c_256'
					],
					{
						'default': 'hyperswap_1a_256'
					}
				),
				'max_workers':
				(
					'INT',
					{
						'default': 16,
						'min': 1,
						'max': 32
					}
				)
			}
		}

	RETURN_TYPES = (IO.VIDEO,)
	FUNCTION = 'process'
	CATEGORY = 'FaceFusion API'

	@staticmethod
	def process(source_image : Tensor, target_video : VideoFromComponents, api_token : str, face_swapper_model : FaceSwapperModel, max_workers : int) -> Tuple[VideoFromComponents]:
		video_components = target_video.get_components()
		output_tensors = []

		swap_face = partial(
			SwapFaceImage.swap_face,
			source_image,
			api_token = api_token,
			face_swapper_model = face_swapper_model
		)

		with ThreadPoolExecutor(max_workers = max_workers) as executor:
			for temp_tensor in executor.map(swap_face, video_components.images):
				temp_tensor = temp_tensor.squeeze(0)[..., :3]
				output_tensors.append(temp_tensor)

		output_video_components = VideoComponents(
			images = torch.stack(output_tensors),
			audio = video_components.audio,
			frame_rate = video_components.frame_rate
		)

		output_video = VideoFromComponents(output_video_components)
		return (output_video,)
