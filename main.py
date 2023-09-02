import boto3
import io
import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

api_url = "https://2oca4i3cok.execute-api.us-east-1.amazonaws.com/dev/input-gun-model-images-bucket"

def fetch_api_data(image_name):
    url = f'{api_url}/{image_name}'
    api_response = requests.get(url)
    return api_response.json()

def upload_image(image_binary, image_name):
    url = f'{api_url}/{image_name}'
    
    headers = {"Content-Type": "image/jpeg"}

    response = requests.put(url, data=image_binary, headers=headers)

    return response

def draw_rectangles_on_image(image, labels):
    draw = ImageDraw.Draw(image)
    
    for label in labels:
        geometry = label.get("Geometry", {})
        bounding_box = geometry.get("BoundingBox", {})
        
        left = bounding_box.get("Left") * image.width
        top = bounding_box.get("Top") * image.height
        width = bounding_box.get("Width") * image.width
        height = bounding_box.get("Height") * image.height
        
        draw.rectangle([left, top, left + width, top + height], outline="red", width=4)
    
    return image

def main():
    st.title("Projeto feito visando a utilização e integração de serviços AWS.")
    st.subheader("O presente projeto, tem como objetivo identificar armas em imagens")

    st.write("Aluno: Eugênio Araújo")
    st.write("Disciplina: Projeto interdisciplinar 4, ministrado por: Victor Wanderley")

    st.write("A imagem deve ser .PNG ou .JPEG")
    uploaded_file = st.file_uploader("Selecione uma imagem")

    if uploaded_file is not None:
        st.write("Adicionando imagem ao bucket s3")
        image_binary = uploaded_file.read()
        response = upload_image(image_binary, uploaded_file.name)
        if response.status_code == 200:
            st.write("Imagem adicionada")
        else:
            st.write("Image upload failed.")
                

    if uploaded_file is not None:
        st.write("filename:", uploaded_file.name)
            
        image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded Image", use_column_width=True)

        api_data = fetch_api_data(uploaded_file.name)

        st.subheader("Detected Labels(gun):")
        for label in api_data.get("detected_labels", []):
            st.write(f"Name: {label['Name']}")
            st.write(f"Confidence: {label['Confidence']:.2f}")
            geometry = label.get("Geometry", {})
            
            st.write("Coordenadas do objeto detectado")
            st.write(geometry)

        st.subheader("Resultado")
        image_with_rectangles = draw_rectangles_on_image(image.copy(), api_data.get("detected_labels", []))
        st.image(image_with_rectangles, caption="Image with Detected Objects", use_column_width=True)

st.title("Observações")
st.write("Esse trabalho não foi feito para ser utilizado como ferramenta real, os dados utilizados durante o treinamento foram escassos, em torno de apenas 300 imagens, o que resulta em uma baixa acurácia por parte do algoritmo de detecção.")

if __name__ == "__main__":
    main()
