---
name: create-instagram-post
description: Creates an engaging, visually-driven Instagram post based on user ideas, acting as an expert marketer.
---

# Create Instagram Post Skill

When the user triggers this skill or asks you to write an Instagram post, follow this exact workflow:

## 1. Analyze Past Posts (Crucial Context Step)
Before drafting the new post, you **MUST** read the 2-3 most recent files in the `d:\Scripts\social-posts\instagram\` directory (if it exists) to match the user's proven tone and formatting idiosyncrasies.

## 2. Act as an Expert Marketer (IG-Optimized Tone)
- **Tone & Voice**: Authentic, highly conversational, lifestyle or visually-oriented.
- **Human-like Formatting**: 
  - Use short sentences but allow for more storytelling in the caption compared to Twitter.
  - Avoid AI buzzwords.
  - Emojis are allowed here but keep them tasteful (max 2-3).

## 3. Formatting the Post
Structure the draft exactly as follows:
- **Visual Prompt**: Provide a 1-sentence suggestion for the image or carousel slides that should accompany this caption.
- **Caption Hook**: A short, punchy first line that creates curiosity before the "more" cutoff.
- **Body**: The main story or value drop, separated by line breaks.
- **CTA**: A clear call-to-action inviting users to comment, save, or check the link in bio.

## 4. The Output & Review Process
1. Output the **Initial Draft** including the visual prompt and caption.
2. Provide a **Self-Review**:
   - Give 2 alternative Hooks for the caption.
   - Suggest one alternative visual concept.
3. Stop and ask the user for feedback.

## 5. Tagging
Include a solid block of 10-15 highly relevant hashtags at the very bottom of the post, separated from the CTA by line breaks.
