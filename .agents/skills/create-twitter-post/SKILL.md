---
name: create-twitter-post
description: Creates an engaging, impression-optimized Twitter post or thread based on user ideas, acting as an expert marketer.
---

# Create Twitter Post Skill

When the user triggers this skill or asks you to write a Twitter post, follow this exact workflow:

## 1. Analyze Past Posts (Crucial Context Step)
Before drafting the new post, you **MUST** read the 2-3 most recent files in the `d:\Scripts\social-posts\twitter\` directory (if it exists) to match the user's proven tone and formatting idiosyncrasies.

## 2. Act as an Expert Marketer (Twitter-Optimized Tone)
- **Tone & Voice**: Punchy, conversational, and highly opinionated or insightful.
- **Human-like Formatting**: 
  - Use extremely short sentences. Often one line per sentence.
  - Avoid formal language and AI buzzwords entirely.
  - Severely restrict emojis (maximum 1 per tweet).

## 3. Formatting the Post
Structure the draft based on the length of the idea:
- **Short Idea (Single Tweet)**:
  - **Hook**: First sentence must create a knowledge gap or state a strong opinion (under 280 characters total).
- **Longer Idea (Thread)**:
  - **Tweet 1 (Hook)**: A scroll-stopping opening line + clear promise of what the thread delivers. End with 🧵 (optional).
  - **Body Tweets**: 1 clear takeaway per tweet. Use line breaks.
  - **Final Tweet (CTA)**: Ask a targeted question to drive replies, or ask for a retweet.

## 4. The Output & Review Process
1. Output the **Initial Draft** (ensure each tweet in a thread is separated by `---`).
2. Provide a **Self-Review**:
   - Give 2 alternative Hooks for the first tweet.
   - Check if any single tweet exceeds 280 characters.
3. Stop and ask the user for feedback.

## 5. Tagging
Include a maximum of 1-2 highly relevant hashtags at the end of the tweet or thread. Provide placeholder tags (e.g. `@[Expert Name]`) if the user mentions specific people.
