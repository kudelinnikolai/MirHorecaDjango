from PIL import Image
from io import BytesIO
import os
import pillow_avif



def set_12_images_from_1(obj):

  imgPath = obj.image.path
  imgFullname = os.path.basename(imgPath)
  imgFolder = os.path.dirname(imgPath)
  imgName = imgFullname.split('.', 1)[0]
  imgExtention = imgFullname.split('.', 1)[1]

  # Проверка на то, есть ли исходное изображение в папке. Если его нет, то это изменение параметра, не относящегося к изображению - тогда пересжимать файлы не надо
  imageFiles = []

  for (dirpath, dirnames, filenames) in os.walk(imgFolder):
    imageFiles.extend(filenames)
    break
  if not imgFullname in imageFiles:
    return
  

  with Image.open(imgPath) as imgMain:
    img1600 = imgMain.convert("RGB")
    img800 = img1600.copy()
    img400 = img1600.copy()
    img70 = img1600.copy()
    img1600.thumbnail((1600,1600))
    img800.thumbnail((800,800))
    img400.thumbnail((400,400))
    img70.thumbnail((70,70))

    # Исходная картинка сжимается с качеством 95% до JPEG, WEBP и AVIF и наибольшей стороной 1600
    imgPath1600 = imgFolder + '/' + imgName    
    img1600.save(imgPath1600 + "_1600.jpg"  , format='JPEG', quality=95)
    img1600.save(imgPath1600 + "_1600.webp", format='WEBP', quality=95)
    img1600.save(imgPath1600 + "_1600.avif", format='AVIF', quality=95)

    # Создание копий 800, 400 и 70 в форматах JPEG WEBP и AVIF
    imgPath800 = imgFolder + '/' + imgName    
    img800.save(imgPath800 + "_800.jpg"  , format='JPEG', quality=95)
    img800.save(imgPath800 + "_800.webp", format='WEBP', quality=95)
    img800.save(imgPath800 + "_800.avif", format='AVIF', quality=95)
    
    imgPath400 = imgFolder + '/' + imgName    
    img400.save(imgPath400 + "_400.jpg"  , format='JPEG', quality=95)
    img400.save(imgPath400 + "_400.webp", format='WEBP', quality=95)
    img400.save(imgPath400 + "_400.avif", format='AVIF', quality=95)
    
    imgPath70 = imgFolder + '/' + imgName    
    img70.save(imgPath70 + "_70.jpg"  , format='JPEG', quality=95)
    img70.save(imgPath70 + "_70.webp", format='WEBP', quality=95)
    img70.save(imgPath70 + "_70.avif", format='AVIF', quality=95)

  # Удаляем нахрен огромный исходный файл
  os.remove(imgPath)



def delete_all_images_with_this_name(obj):

  imgPath = obj.image.path
  imgFolder = os.path.dirname(imgPath)
  imgName = os.path.basename(imgPath).split('.', 1)[0]

  imageFiles = []

  for (dirpath, dirnames, filenames) in os.walk(imgFolder):
    imageFiles.extend(filenames)
    break

  for file in imageFiles:
    if file.rsplit('_', 1)[0] == imgName:
      os.remove(imgFolder + '/' + file)
    if file == os.path.basename(imgPath):
      os.remove(imgFolder + '/' + file)





def get_small_image_url(imgUrl, px, ext):
  imgFolder = os.path.dirname(imgUrl)
  imgName = os.path.basename(imgUrl).split('.', 1)[0]
  return(imgFolder + '/' + imgName + '_' + px + '.' + ext)