
import os
import random
from PIL import Image
from torchvision import transforms
from tqdm import tqdm


class ImageAugment:

    def __init__(self, input_dir='dataset', output_dir='dataset_augmented', target_num_per_class=6):

        # 配置
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_num_per_class = target_num_per_class  # 每类目标图像数量

        # 定义增强操作（不裁剪、不缩放）
        self.augmentation_transforms = transforms.Compose([
            transforms.RandomRotation(degrees=10),  # 小角度旋转
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 1.0)),
            transforms.RandomHorizontalFlip(p=0.5),
        ])

    def random_scale(self, img, scale_range=(0.8, 1.2)):

        """
        按比例随机缩放图像，保持纵横比。
        scale_range: 缩放比例范围，例如0.8到1.2倍。
        """
        w, h = img.size
        scale = random.uniform(*scale_range)
        new_w = int(w * scale)
        new_h = int(h * scale)
        scaled_img = img.resize((new_w, new_h), Image.BILINEAR)
        return scaled_img

    def augment(self):

        # 创建输出文件夹
        os.makedirs(self.output_dir, exist_ok=True)

        for class_name in tqdm(os.listdir(self.input_dir), desc="Processing classes"):
            class_path = os.path.join(self.input_dir, class_name)
            output_class_path = os.path.join(self.output_dir, class_name)
            os.makedirs(output_class_path, exist_ok=True)

            images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

            all_images = []
            for img_name in images:
                img_path = os.path.join(class_path, img_name)
                img = Image.open(img_path).convert('RGB')
                all_images.append(img)
                save_path = os.path.join(output_class_path, img_name)
                img.save(save_path)

            # 开始增强
            img_idx = 0
            while len(os.listdir(output_class_path)) < self.target_num_per_class:
                src_img = all_images[img_idx % len(all_images)]

                scaled_img = self.random_scale(src_img, scale_range=(0.8, 1.2))

                aug_img = self.augmentation_transforms(scaled_img)

                save_name = f"{images[img_idx % len(all_images)].split('.')[0]}_aug{random.randint(1000, 9999)}.jpg"
                aug_img.save(os.path.join(output_class_path, save_name))
                img_idx += 1

        print("✅ 增强完成：每类图像已扩展到 6 张")
