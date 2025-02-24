import streamlit as st
import requests
import io
from PIL import Image
import base64
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Image Generator",
    page_icon="🎨",
    layout="centered"
)

# App title and description
st.title("🎨 AI Image Generator")
st.markdown("Generate images from text prompts using Stable Diffusion")

# Sidebar for API settings
with st.sidebar:
    st.header("Settings")
    
    # API token input - users will need to enter this each time they use the app
    api_token = st.text_input(
        "Hugging Face API Token", 
        type="password", 
        help="Enter your Hugging Face API token. Get one at huggingface.co/settings/tokens"
    )
    
    # Show token instructions if not provided
    if not api_token:
        st.info("ℹ️ You'll need a Hugging Face API token to use this app.")
        st.markdown("""
        **How to get a token:**
        1. Create an account at [huggingface.co](https://huggingface.co/join)
        2. Go to Settings → Access Tokens
        3. Create a new token with 'read' scope
        """)
    
    st.subheader("Model Options")
    model_id = st.selectbox(
        "Choose a model",
        [
            "stabilityai/stable-diffusion-2-1",
            "runwayml/stable-diffusion-v1-5",
            "CompVis/stable-diffusion-v1-4",
            "prompthero/openjourney"
        ]
    )
    
    st.markdown("---")
    st.markdown("Made with Streamlit and Hugging Face")

# Main content
st.header("Create Your Image")

# Text prompt input
prompt = st.text_area(
    "Enter your prompt", 
    placeholder="A futuristic cityscape with flying cars and neon lights, digital art",
    help="Describe the image you want to generate. Be specific for better results."
)

# Advanced options collapsible section
with st.expander("Advanced Options"):
    col1, col2 = st.columns(2)
    with col1:
        num_steps = st.slider("Inference Steps", min_value=20, max_value=100, value=50, help="More steps = higher quality but slower")
    with col2:
        guidance_scale = st.slider("Guidance Scale", min_value=1.0, max_value=20.0, value=7.5, step=0.5, help="How closely to follow the prompt")

# Function to generate image
def generate_image(prompt, model_id, api_token, num_steps=50, guidance_scale=7.5):
    """Generate an image using Stable Diffusion via Hugging Face Inference API"""
    
    # API endpoint
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    # Headers with authorization
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    
    # Data payload with the prompt
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": num_steps,
            "guidance_scale": guidance_scale,
        }
    }
    
    # Make API request
    with st.spinner("AI is creating your image..."):
        response = requests.post(api_url, headers=headers, json=payload)
    
    # Handle the response
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        return image, None
    else:
        if "waiting for the model to be loaded" in response.text.lower():
            return None, "Model is still loading. Please wait a moment and try again."
        else:
            return None, f"Error: {response.status_code}\n{response.text}"

# Generate button and history
if st.button("Generate Image", type="primary", disabled=not api_token or not prompt):
    if not api_token:
        st.error("Please enter your Hugging Face API token in the sidebar.")
    elif not prompt:
        st.error("Please enter a prompt to generate an image.")
    else:
        # Call the generate function
        image, error = generate_image(
            prompt=prompt, 
            model_id=model_id, 
            api_token=api_token,
            num_steps=num_steps,
            guidance_scale=guidance_scale
        )
        
        # Display image or error
        if image:
            # Store in session state to keep it visible
            st.session_state.last_image = image
            st.session_state.last_prompt = prompt
        elif error:
            st.error(error)

# Display the last generated image
if 'last_image' in st.session_state:
    st.header("Your Generated Image")
    st.image(st.session_state.last_image, caption=st.session_state.last_prompt, use_column_width=True)
    
    # Add download button
    buf = io.BytesIO()
    st.session_state.last_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download Image",
            data=byte_im,
            file_name=f"ai_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            mime="image/png"
        )
    with col2:
        if st.button("Create New Image"):
            # Clear the displayed image to focus on creating a new one
            st.session_state.pop('last_image', None)
            st.session_state.pop('last_prompt', None)
            st.rerun()

# Tips section
if 'last_image' not in st.session_state:
    with st.expander("💡 Tips for better prompts"):
        st.markdown("""
        - Be specific about what you want to see
        - Mention the style (painting, digital art, photograph, etc.)
        - Include details about lighting, color scheme, and mood
        - Example: "A serene Japanese garden with a koi pond, cherry blossoms, soft morning light, studio ghibli style"
        """)

# Help section
with st.expander("❓ Need Help?"):
    st.markdown("""
    **Common issues:**
    
    1. **"Model is still loading"**: The model is being loaded on Hugging Face's servers. Wait a minute and try again.
    
    2. **API Token errors**: Make sure you've entered your token correctly. It should start with "hf_".
    
    3. **Slow generation**: Free tier has lower priority. Advanced options like increasing steps will also slow down generation.
    
    4. **Usage limits**: The free tier has usage limits. If you hit them, you may need to wait or upgrade.
    """)