import os

import fitz


def convert_pdf_to_png(pdf_file_path, png_path):
    """
    Convert a single PDF file to PNG image with specific cropping parameters.
    
    Args:
        pdf_file_path (str): Path to the input PDF file
        png_path (str): Path where the output PNG file will be saved
    """
    ref_doc_total_width_cm = 29.0
    ref_doc_total_height_cm = 41.5

    crop_width_start_cm = (8/12) * ref_doc_total_width_cm  # (9-1)/12 * 29.0 cm = 19.333 cm
    crop_width_end_cm = (12/12) * ref_doc_total_width_cm # 12/12 * 29.0 cm = 29.0 cm

    crop_height_start_cm = 0.035 * ref_doc_total_height_cm  # 0.08 * 41.5 cm = 3.32 cm
    crop_height_end_cm = 0.68 * ref_doc_total_height_cm   # 0.72 * 41.5 cm = 29.88 cm

    output_dpi = 300  # DPI for the output PNG images (higher DPI = better quality)

    print("--- 裁剪参数 (厘米) ---")
    print(f"  页面总宽度: {ref_doc_total_width_cm} cm, 页面总高度: {ref_doc_total_height_cm} cm")
    print(f"  裁剪宽度: 从 {crop_width_start_cm:.3f} cm 到 {crop_width_end_cm:.3f} cm")
    print(f"  裁剪高度: 从 {crop_height_start_cm:.3f} cm 到 {crop_height_end_cm:.3f} cm")
    print("-------------------------")

    try:
        if ref_doc_total_width_cm <= 0 or ref_doc_total_height_cm <= 0:
            print("错误：参考文档的宽度或高度必须大于零。请检查配置。")
            return

        prop_x0 = crop_width_start_cm / ref_doc_total_width_cm
        prop_y0 = crop_height_start_cm / ref_doc_total_height_cm
        prop_x1 = crop_width_end_cm / ref_doc_total_width_cm
        prop_y1 = crop_height_end_cm / ref_doc_total_height_cm
    except ZeroDivisionError:
        print("错误：参考文档的宽度或高度理论上不应为零。")
        return

    if not (prop_x0 < prop_x1 and prop_x0 >= -0.00001 and prop_x1 <= 1.00001 and \
            prop_y0 < prop_y1 and prop_y0 >= -0.00001 and prop_y1 <= 1.00001):
        print("错误：计算出的裁剪比例无效。请检查厘米值是否在文档范围内且起始值小于结束值。")
        print(f"  prop_x0: {prop_x0:.4f}, prop_x1: {prop_x1:.4f}")
        print(f"  prop_y0: {prop_y0:.4f}, prop_y1: {prop_y1:.4f}")
        return

    # 确保输出目录存在
    png_dir = os.path.dirname(png_path)
    if not os.path.exists(png_dir):
        os.makedirs(png_dir)
        print(f"已创建输出目录: {png_dir}")

    print(f"正在处理PDF文件: {pdf_file_path}")

    try:
        doc = fitz.open(pdf_file_path)
        if doc.page_count == 0:
            print(f"  警告: 文件不包含任何页面。")
            return

        # 只处理第一页
        page = doc.load_page(0)
        page_rect = page.rect
        page_width_points = page_rect.width
        page_height_points = page_rect.height

        clip_x0 = page_width_points * prop_x0
        clip_y0 = page_height_points * prop_y0
        clip_x1 = page_width_points * prop_x1
        clip_y1 = page_height_points * prop_y1

        crop_area = fitz.Rect(clip_x0, clip_y0, clip_x1, clip_y1)

        if not crop_area.is_valid or crop_area.is_empty:
            print("  警告: 裁剪区域无效或为空。")
            return
        
        crop_area.intersect(page_rect) #确保裁剪区域不超过页面边界
        if crop_area.is_empty:
            print("  警告: 裁剪区域与页面无交集。")
            return

        pix = page.get_pixmap(clip=crop_area, dpi=output_dpi)
        pix.save(png_path)
        print(f"\n处理完成。已保存PNG文件: {png_path}")

        doc.close()
        return png_path
    except fitz.fitz.FZ_ERROR_GENERIC as e:
        print(f"  错误: 处理文件时发生 PyMuPDF 错误: {e}")
    except Exception as e:
        print(f"  错误: 处理文件时发生未知错误: {e}")