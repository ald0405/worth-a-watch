import streamlit as st
# from google import genai
from config import YouTubeSummary,client,People
import datetime

# Streamlit UI
st.title("🎬 Worth the Watch? – Let AI help you decide!")

# Input field for YouTube URL
youtube_url = st.text_input("Enter the YouTube URL")

# Create columns
col1, col2 = st.columns([1, 2])

if youtube_url:
    youtube_analyser = YouTubeSummary(client, youtube_url)
    youtube_analyser._fetch_metadata()

    if youtube_analyser.contextual_metadata:
        metadata = youtube_analyser.contextual_metadata

        with col1:
            if metadata.get("thumbnail"):
                st.image(metadata["thumbnail"], use_container_width=True)
            else:
                st.warning("⚠️ No thumbnail available for this video.")

        with col2:
            st.subheader(metadata["title"])
            # st.write(f"📅 **Upload Date:** {metadata['upload_date'].strftime('%A %d %B %Y')}")
            st.write(f"📅 **Upload Date:** {datetime.datetime.strptime(metadata['upload_date'], '%Y%m%d'):%A %d %B %Y}")
            st.write(f"👤 **Uploader:** [{metadata['uploader']}]({metadata['channel_url']})")
            st.write(f"👀 **Views:** {metadata['view_count']:,}")
            st.write(f"👍 **Likes:** {metadata['like_count']:,}")
            st.write(f"📢 **Categories:** {', '.join(metadata['categories']) if metadata['categories'] else 'N/A'}")    
        with st.expander("🔍 Show Full Description"):
            st.write(metadata["description"])



        # Generate AI Summary
        with st.spinner("Generating AI-powered summary...",show_time=True):
            summary = youtube_analyser.generate_summary()

        if summary:
            st.subheader(f"**Video Details**")

            st.subheader("👥 **People in the Video**")
            for person in summary.people:
                if person.background:
                    st.write(f"👤 **{person.name}** - {person.background}")
                else:
                    st.write(f"👤 **{person.name}**")  # No background available

            st.subheader("📜 **Summary**")
            st.text("AI-Generated Please Interpret with Caution")
            st.write(summary.video_summary)

        else:
            st.error("⚠️ Failed to generate AI summary.")

