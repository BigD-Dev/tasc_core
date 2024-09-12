import requests
from PIL import Image
from io import BytesIO
import numpy as np
from sklearn.cluster import KMeans, MeanShift
from sklearn.metrics import silhouette_score
import cv2


class ImageProcessor:
    def __init__(self, num_colors=3):
        self.num_colors = num_colors

    def fetch_image_from_url(self, image_url):
        """Fetches an image from a given URL."""
        response = requests.get(image_url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            return image
        else:
            raise Exception(f"Failed to fetch image. Status code: {response.status_code}")

    def load_image_from_path(self, image_path):
        """Loads an image from a local file path."""
        return Image.open(image_path)

    def pre_process_image(self, image):
        """
        Pre-processes the image:
        - Resizes to reduce noise and processing time
        - Converts to Lab color space for better perceptual clustering
        """
        # Resize the image to a fixed size
        image = image.resize((150, 150))

        # Convert to numpy array and convert to Lab color space
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2LAB)

        # Reshape the image to a 2D array of pixels
        image_reshaped = image_cv.reshape((image_cv.shape[0] * image_cv.shape[1], 3))
        return image_reshaped

    def find_optimal_clusters(self, image, max_clusters=10):
        """Finds the optimal number of clusters based on silhouette score."""
        processed_image = self.pre_process_image(image)
        best_num_clusters = 2
        best_score = -1

        for n_clusters in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=n_clusters)
            labels = kmeans.fit_predict(processed_image)

            score = silhouette_score(processed_image, labels)
            if score > best_score:
                best_num_clusters = n_clusters
                best_score = score

        self.num_colors = best_num_clusters
        return best_num_clusters

    def get_dominant_colors_kmeans(self, image):
        """Finds the dominant colors in the image using KMeans clustering."""
        processed_image = self.pre_process_image(image)

        # Fit KMeans to the processed image
        kmeans = KMeans(n_clusters=self.num_colors)
        kmeans.fit(processed_image)

        # Extract the cluster centers (dominant colors)
        colors = kmeans.cluster_centers_[:, :3].astype(int)  # Use only LAB colors
        return [tuple(color) for color in colors]

    def get_dominant_colors_meanshift(self, image):
        """Uses MeanShift clustering to find dominant colors."""
        processed_image = self.pre_process_image(image)

        # Fit MeanShift to the image
        meanshift = MeanShift()
        meanshift.fit(processed_image)

        # Extract the cluster centers (dominant colors)
        colors = meanshift.cluster_centers_[:, :3].astype(int)  # Use only LAB colors
        return [tuple(color) for color in colors]

    def colors_to_hex(self, colors):
        """Converts LAB colors to RGB and then to hexadecimal."""
        hex_colors = []
        for color in colors:
            lab_color = np.uint8([[list(color)]])
            rgb_color = cv2.cvtColor(lab_color, cv2.COLOR_LAB2RGB)[0][0]
            hex_colors.append('#{:02x}{:02x}{:02x}'.format(rgb_color[0], rgb_color[1], rgb_color[2]))
        return hex_colors

    def extract_colors(self, image_url=None, image_path=None, use_meanshift=False):
        """
        Full process to extract the best 3 dominant colors:
        - Can fetch from URL or load from path
        - Uses KMeans as the default, can use MeanShift if specified
        """
        if image_url:
            image = self.fetch_image_from_url(image_url)
        elif image_path:
            image = self.load_image_from_path(image_path)
        else:
            raise Exception("No image source provided!")

        # Find the optimal number of clusters using silhouette score
        optimal_clusters = self.find_optimal_clusters(image)
        print(f"Optimal number of clusters: {optimal_clusters}")

        # Get dominant colors using the selected clustering algorithm
        if use_meanshift:
            colors = self.get_dominant_colors_meanshift(image)
        else:
            colors = self.get_dominant_colors_kmeans(image)

        # Convert colors to hex
        hex_colors = self.colors_to_hex(colors)

        # Return only the top 3 dominant colors in hex format
        return hex_colors[:3]


# Example usage
if __name__ == "__main__":
    processor = ImageProcessor()

    # Fetch the image from a URL
    image_url = "https://cdn.shopify.com/s/files/1/0327/7452/0971/files/neptuneteefinal.jpg?v=1720963628"

    try:
        hex_colors = processor.extract_colors(image_url=image_url)
        print(f"Top 3 Dominant Colors (Hex): {hex_colors}")
    except Exception as e:
        print(e)