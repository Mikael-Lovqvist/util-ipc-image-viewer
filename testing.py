from PIL import Image, ImageDraw
from colorsys import hls_to_rgb, hsv_to_rgb
import random, time

def hls(h, l, s):
	rgb = hls_to_rgb(h, l, s)
	irgb = tuple(min(255, max(0, int(component * 255))) for component in rgb)
	return irgb

def generate_random_images(count=None):
	while count is None or count > 0:

		if count is not None:
			count -= 1

		width = random.randint(1, 1024)
		height = random.randint(1, 1024)

		image = Image.new('RGB', (width, height))

		draw = ImageDraw.Draw(image)

		polygon_count = random.randint(1, 50)

		for p in range(polygon_count):
			max_radius = min(width, height) / 3
			x = random.randint(0, width-1)
			y = random.randint(0, height-1)
			r = random.uniform(5, max_radius)
			w = random.uniform(0, 0.2) * r
			sides = random.randint(3, 12)
			rotation = random.uniform(-180, 180)

			fill_color = hls(random.uniform(0, 1), random.uniform(0.5, 1.0), random.uniform(0.0, 1.0))
			stroke_color = hls(random.uniform(0, 1), random.uniform(0.0, 0.3), random.uniform(0.0, 1.0))
			draw.regular_polygon((x, y, r), sides, rotation, fill=fill_color, outline=stroke_color)

		yield image



def show_images(window, frequency):

	for image in generate_random_images():
		window.new_pil_image(image)
		time.sleep(1.0 / frequency)
