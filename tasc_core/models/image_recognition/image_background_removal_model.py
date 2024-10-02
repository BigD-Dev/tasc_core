import torch
import numpy as np
import cv2
import os
import io
from PIL import Image
from backgroundremover.bg import remove
# U2Net model definition (download this from the U2Net GitHub repo)
from U2Net.model import U2NET  # This assumes you have the u2net.py in the U2Net/model directory

# Image preprocessing function
def normalize(image):
    image = np.array(image).astype(np.float32)
    tmpImg = np.zeros((image.shape[0], image.shape[1], 3))
    image = image / np.max(image)
    tmpImg[:, :, 0] = (image[:, :, 0] - 0.485) / 0.229
    tmpImg[:, :, 1] = (image[:, :, 1] - 0.456) / 0.224
    tmpImg[:, :, 2] = (image[:, :, 2] - 0.406) / 0.225
    tmpImg = tmpImg.transpose((2, 0, 1))
    return tmpImg


# Post-process the output to a binary mask
def save_output(image_name, pred, output_dir):
    pred = pred.squeeze()
    pred = pred.cpu().data.numpy()
    mask = np.where(pred > 0.5, 255, 0).astype(np.uint8)

    # Load the original image and apply the mask
    original_image = cv2.imread(image_name)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    mask = cv2.resize(mask, (original_image.shape[1], original_image.shape[0]))

    # Convert mask to 3 channels
    mask = np.stack((mask,) * 3, axis=-1)

    # Apply the mask to the original image
    result = cv2.bitwise_and(original_image, mask)

    # Save the masked image
    cv2.imwrite(output_dir, result[:, :, ::-1])


# Load the model
def load_model(model_path):
    print("Loading U2Net model...")
    model = U2NET(3, 1)  # Initialize U2Net model
    if torch.cuda.is_available():
        model.load_state_dict(torch.load(model_path))
        model = model.cuda()
    else:
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    return model


# Perform background removal
def remove_background(model, image_path, output_path):
    image = Image.open(image_path)
    image = image.convert("RGB")

    # Preprocess the image
    image = normalize(image)
    image = torch.from_numpy(image).unsqueeze(0).float()

    if torch.cuda.is_available():
        image = image.cuda()

    with torch.no_grad():
        d1, d2, d3, d4, d5, d6, d7 = model(image)
        mask = d1[:, 0, :, :]
        save_output(image_path, mask, output_path)

def remove_bg(src_img_path, out_img_path):
    model_choices = ["u2net", "u2net_human_seg", "u2netp"]

    # Check if the source image file exists
    if not os.path.exists(src_img_path):
        raise FileNotFoundError(f"Source image file not found: {src_img_path}")

    # Read the image data
    with open(src_img_path, "rb") as f:
        data = f.read()

    # Verify the image data
    try:
        # Check if the image data can be opened by PIL
        Image.open(io.BytesIO(data)).verify()

        img = remove(data, model_name=model_choices[0],
                     alpha_matting=True,
                     alpha_matting_foreground_threshold=240,
                     alpha_matting_background_threshold=10,
                     alpha_matting_erode_structure_size=10,
                     alpha_matting_base_size=1000)
    except Exception as e:
        raise ValueError(f"Error processing image data: {e}")

    # Write the output image
    with open(out_img_path, "wb") as f:
        f.write(img)

if __name__ == "__main__":
    # Path to the U2Net pre-trained model weights
    # model_path = "../saved_models/u2net.pth"  # Path to the u2net.pth file
    image_name = "never-fully-dressed-angel-mesh-top-5"
    image_path = f"{image_name}.png"  # Path to the input image
    output_path = f"{image_name}_op.png"  # Path to save the output image with background removed

    remove_bg(image_path, output_path)

