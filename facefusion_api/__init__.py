from .core import SwapFaceImage, SwapFaceVideo
from .types import NodeClassMapping, NodeDisplayNameMapping

NODE_CLASS_MAPPINGS : NodeClassMapping =\
{
	'SwapFaceImage': SwapFaceImage,
	'SwapFaceVideo': SwapFaceVideo
}

NODE_DISPLAY_NAME_MAPPINGS : NodeDisplayNameMapping =\
{
	'SwapFaceImage': 'Image Swap Face',
	'SwapFaceVideo': 'Video Swap Face'
}
