from PIL import Image, ImageDraw, ImageFont

def prepare_linkedin_image(
        image_path,
        output_path,
        center_text,
        right_text="YourBrand",
        font_path="arial.ttf",
        font_size=36
):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size

    # Target 16:9 crop centered (from chatgpt)
    target_ratio = 16 / 9
    new_w = w
    new_h = int(w / target_ratio)
    if new_h > h:
        new_h = h
        new_w = int(h * target_ratio)

    left = (w - new_w) // 2
    top = (h - new_h) // 2
    img_cropped = img.crop((left, top, left + new_w, top + new_h))

    draw = ImageDraw.Draw(img_cropped)
    font = ImageFont.truetype(font_path, font_size)
    padding_x, padding_y = 16, 16
    text_area_height = font_size + 2 * padding_y
    img_w, img_h = img_cropped.size
    rect_y0 = img_h - text_area_height
    rect_y1 = img_h
    draw.rectangle([(0, rect_y0), (img_w, rect_y1)], fill="white")

    center_text_size = draw.textbbox((0, 0), center_text, font=font)
    center_text_width = center_text_size[2] - center_text_size[0]
    center_text_x = (img_w - center_text_width) // 2
    center_text_y = rect_y0 + padding_y
    draw.text((center_text_x, center_text_y), center_text, font=font, fill="black")

    right_text_size = draw.textbbox((0, 0), right_text, font=font)
    right_text_width = right_text_size[2] - right_text_size[0]
    right_text_x = img_w - right_text_width - padding_x
    right_text_y = rect_y0 + padding_y
    draw.text((right_text_x, right_text_y), right_text, font=font, fill="black")

    img_cropped.save(output_path)
