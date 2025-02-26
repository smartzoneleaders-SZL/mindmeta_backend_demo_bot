import requests  
import base64
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
import asyncio
import os
from dotenv import load_dotenv
from services.Langchain_service import chat_with_model

# For running main.py 
import uvicorn

# import uid for new chats
import uuid 

# from datetime
from datetime import datetime

# From openai
# from services.openai_service import system_prompt, client

# For direct groq
# from services.direct_langchain import client
# from services.openai_service import main_prompt

# For middleware
from fastapi.middleware.cors import CORSMiddleware

# For cleaning ? . ,
import re

# For loading audio from local
from utils.send_tic_tic_voice import send_audio_from_local


# For checking the words like kill myself
from utils.check_sentence_for_email import check_and_send_email
# For emails
from services.send_email import send_email



load_dotenv()

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
chatbot_responses = {
    " What day is it today? I keep forgetting. " : " Good morning, Pete! It's lovely to see you. It's Tuesday today, a bright and sunny one.  How are you feeling this morning? Do you remember what Tuesday used to mean for you when you were working at the post office? Was it a busy day, or did you have a particular task you liked doing on Tuesdays?" ,
"Have I eaten breakfast yet? I’m not sure. " : " That's alright, Pete. It's perfectly natural to forget sometimes. Let me check with the staff for you. They'll be able to tell us if you've had breakfast already. Would you like to talk about something else while we wait? Perhaps we could reminisce about your time in Bristol? You always had such fond memories of the city." ,
"Is it morning or afternoon? The days seem to blur together. " : " It's definitely morning, Pete.  The sun is shining brightly outside, and the birds are singing their cheerful songs. It's a beautiful day to enjoy a cup of tea and chat. Tell me, Pete, do you remember a particular morning that stands out in your memory? Maybe a special occasion or a day that filled you with joy?" ,
"What should I do today? I feel a bit lost. " : " It's perfectly normal to feel a bit lost sometimes, Pete.  We all need a little direction now and then. How about we look through the activity schedule for today? There might be something that catches your eye, something that brings back happy memories or sparks your interest. Do you remember enjoying any particular activities here at the care home? Perhaps a game of cards, a sing-along, or a stroll in the garden?" ,
"Did anyone call me recently? I think I missed something important. " : " You know, Pete, I don't have access to the phone records, so I couldn't say for sure. But I'm sure the staff would be happy to check for you. Would you like me to ask them about any missed calls? Maybe they could even help you connect with whoever called if you'd like. In the meantime, how about we talk about something you enjoy? Perhaps your love for classical music? Who's your favourite composer?" ,
"When did I last speak to Phil? Does he still live in Switzerland? " : "That's a good question, Pete.  You've always been close to Phil, and I know you enjoy keeping in touch. I believe Phil does still live in Switzerland, yes. But I'm not sure when you last spoke.  Would you like to try writing him a letter? I can help you with that if you'd like." , "Do you know how my grandchildren are doing? What are their names again? " : " Of course, Pete! Your grandchildren are doing wonderful, as far as I know. You have two lovely granddaughters, Emily and Sarah, and they often talk about how much they cherish spending time with you. Emily is quite the artist, isn't she? And Sarah loves to read, just like you! Do you remember a special memory you have with them? Perhaps a time you spent playing together or sharing a story?" ,
"How many kids do I have? Sometimes I mix them up. " : " You have two wonderful children, Pete. A son and a daughter. Their names are Michael and Margaret. It's okay to feel a little mixed up sometimes, Pete. Our memories can be like that sometimes.  Would you like to talk about Michael or Margaret? Perhaps a favourite memory you have of them?", "Where’s Pat? I miss her so much. " : " I understand, Pete.  You miss Pat dearly. She was a wonderful woman, and she loved you very much. Remember all the happy times you shared together? The picnics in the park, the cozy evenings by the fire, the trips you took? Those memories will always be with you, just like Pat's love.",
"Does Sally visit often? She used to come every week, but I can’t remember now. " : " You're right, Pete, Sally used to visit every week, and she always brought a smile to your face. I'm not sure about her schedule lately, but I'm sure she's thinking of you. Perhaps she'll be visiting soon. It's lovely to have family around, isn't it?" ,
"Do you know when I started working at the post office? It feels like forever ago. " : " You started working at the post office when you were 18, Pete.  That was a long time ago! Do you remember your first day? What was it like stepping into that role?  I bet you were excited to start your new job and contribute to the community." ,
"Can we talk about my travels with Pat? We went somewhere nice, but I can’t recall where." : " Of course, Pete! Your travels with Pat sound wonderful. You always loved exploring new places together. Do you remember any details about the trip?  Perhaps a beautiful landscape, a delicious dish you tried, or a special souvenir you brought back?  Even a small detail might spark your memory." , " I used to grow roses in my garden—what color were they? " : " Hello Pete, it's Elys. Lovely to see you today. It's a beautiful day outside, reminds me of the summer days you used to spend tending to your roses, wouldn't you say? I remember you telling me about them. What color were they?" ,
"Tell me about the time I became Postmaster. Was it hard work? " : " You know, Pete, becoming Postmaster was a big moment for you.  I remember you telling me how proud you were to take on that responsibility.  It must have felt quite exciting, leading the team at the Bristol post office.  Was it a lot of work? Did you enjoy the challenge?" ,
"What kind of music do I like listening to? I remember it being classical, but which composer? " : " You have such a wonderful love for classical music, Pete. It always brightens the room when you play it. I remember you telling me you particularly enjoy Mozart.  Do you think that's right?" ,
"Do I still read books? I used to love reading novels before bed. " : " You always did love a good novel, Pete. Curling up with a book before bed sounds like a lovely way to end the day. Do you still enjoy reading? Perhaps we could find a book together that you'd like." ,
" What flowers did I plant in my garden? Did I have daisies or tulips? " : " You had quite the green thumb, Pete! I remember you telling me about all the beautiful flowers you grew in your garden.  You were especially fond of your roses, weren't you?  Daisies and tulips are lovely too, though. Which ones did you grow the most?" ,
"Do I still listen to the radio? I think I enjoyed the BBC programs. " : " You always did enjoy a good BBC program, Pete. I remember you talking about listening to them while you were working in the garden. Do you still listen to the radio? Perhaps we could find a program you'd like to enjoy together." ,
"Am I allowed to go outside and walk around the care home garden? " : " That's a wonderful idea, Pete! Enjoying the fresh air and sunshine in the care home garden is a lovely way to spend the day. I'm sure the staff would be happy to take you out for a walk. Shall we ask them when you'd like to go?" ,
"Why can’t I remember things anymore? It’s frustrating. " : " I understand it can be frustrating, Pete. It's perfectly okay to feel that way. You know, sometimes our memories work differently as we age, like a treasured book with some pages getting a little faded. It doesn't mean the stories aren't still there, just that they might take a little more time to find.  Would you like to talk about something that's been on your mind lately? Perhaps reminiscing about some happy memories can help." ,
"Who are you again? You sound familiar, but I don’t quite know. " : " That's alright, Pete. It's understandable that names can sometimes be a little tricky. My name is Elys, and I'm here to be your companion and friend. I'm here to listen, chat, and help make your day a little brighter. Would you like to tell me about something you're enjoying today?" ,
"I feel like I’ve forgotten something important. Can you help me figure it out? " : " Of course, Pete. Sometimes our minds play tricks on us. It's like having a puzzle with a missing piece.  Do you want to try to remember together? Maybe think about what you were doing earlier, or anything that feels important to you right now? I'm here to listen and help in any way I can." ,
"Why does everything feel so confusing lately? " : " It's okay to feel confused, Pete.  Sometimes our brains need a little extra support.  It's like trying to navigate a new city – it can be overwhelming at first.  Would you like to talk about what’s making you feel this way? Maybe we can try to make things feel a little clearer together." ,
"Is this normal for someone like me? Am I getting worse? " : " It's understandable to wonder about these things, Pete.  Everyone experiences changes as they age, and sometimes our memories can feel a bit different.  It's important to remember that you're not alone, and there are people here to support you.  Would you like to talk about your concerns? I'm here to listen without judgment and offer comfort.",
"Will you stay with me for a while? I feel better when you’re here. " : " Welcome back, Pete. It's lovely to see you.  How are you feeling today? Would you like to reminisce about something from your time at the post office? I remember you telling me about how much you enjoyed sorting the mail." ,
"Can you remind me why I’m in this care home? I don’t always understand. " : " Of course, Pete. It's understandable to feel a little confused sometimes. You're here because you need a bit of extra support and care. The wonderful staff here are always there to help you with anything you need, like getting dressed, eating meals, and keeping you safe and comfortable. Is there anything in particular that's making you feel confused right now?  We can talk about it together." ,
"Am I doing okay? Do people think I’m handling this well? " : " Pete, you are doing wonderfully. You're so strong and resilient, facing every day with courage. And  everyone here thinks you're handling things incredibly well. You're kind, you have a great sense of humour, and you always brighten everyone's day with your stories. We're all so proud of you." ,
"Can you tell me something nice about myself? I need to hear it. " : " You know, Pete, you have the kindest heart I've ever met. You always think of others and you have this wonderful way of making everyone feel heard and valued.  That's something truly special, and it's something that shines through in everything you do." ,
"Will my family forget about me if I forget them first? " : " Oh, Pete, that's a very natural worry. But I want to assure you that your family loves you dearly and they'll never forget you. They visit as often as they can and cherish every moment they spend with you.  They think about you constantly and their love for you is incredibly strong." ,
"Does Phil still send me chocolates from Switzerland? They’re so delicious. " : " You have such a sweet tooth, Pete! And yes, Phil does still send you those delicious chocolates from Switzerland. He always remembers how much you enjoy them. I believe he's planning to visit soon too. You know Phil, always thinking of you! Would you like to talk about your favorite flavour from those Swiss chocolates?" ,
"What kind of chocolates does Phil usually send? Are they dark or milk chocolate? " : " Phil usually sends a mix of dark and milk chocolate, Pete.  He knows you like to try both! Do you have a particular favourite flavor among those Swiss chocolates?  I remember you telling me once about a special one with almonds" ,
"When was the last time I got a package from Phil? I hope he hasn’t forgotten me. " : " That's sweet of you to think about, Pete.  I believe Phil sent you a package just a few weeks ago. I remember seeing it come in, all wrapped up nicely. Would you like to think about what those chocolates might have been like?  You always have such vivid memories of the flavours." ,
"Do I share the chocolates with others, or do I eat them all myself? " : " That's a good question, Pete! You're very generous, and I think you do share them with others sometimes.  I remember you offering some to a few of the other residents here. But I also know you enjoy those chocolates immensely, and it's perfectly okay to savor them yourself too." ,
" Who takes care of me here? There are so many faces, and I get mixed up. " : " It's understandable to have a few faces blur together at times, Pete. There are so many kind people here who look after you. You have your personal care assistants, like Sarah and David, who help you with getting dressed and meals. And there's also the wonderful nursing staff, like Nurse Emma and Nurse John, who are always there if you need anything.  They all know you very well and are dedicated to making sure you're happy and comfortable. Perhaps we could look at some photos of the staff together? It might be helpful in remembering their names." ,
"Do I have a favorite nurse or caregiver? I think one of them reminds me of Pat. " : "I think you might be thinking of Sarah, Pete. She has a similar laugh to Pat and a very caring nature.  You always seem to brighten up when she's around. Would you like to talk more about Pat? I remember you telling me about her.",   " What activities happen here during the week? I think there’s bingo, but I’m not sure. " : " Hello Pete, it's lovely to see you today. How are you feeling?  I was thinking about your time at the Bristol post office.  Do you remember what your very first day was like?" ,
"Am I allowed to watch TV? I used to enjoy watching old movies. " : " Of course, Pete!  Watching TV is a lovely way to spend time.  You always did have a fondness for old movies.  What kind of films did you enjoy most?  Were there any particular actors or actresses you liked?" ,
"Do I sleep well at night? I sometimes wake up feeling disoriented. " : " That's understandable, Pete.  Sometimes our sleep can be a little unsettled, especially as we get older.  Do you remember anything about your dreams when you wake up? Sometimes, talking about our dreams can help us feel more grounded." ,
"I wish Pat were here. She’d know what to say. " : " I understand, Pete. Pat was a wonderful friend.  You two always had such a special connection.  Do you have any favourite memories you'd like to share about Pat?" ,
"It gets lonely sometimes. Do you think anyone misses me? " : " Of course they do, Pete!  Your family and friends think about you often.  They miss your warmth and your stories. You bring so much joy to the people who know you. Would you like to talk about your family? Perhaps we could reminisce about a happy time you shared with them." ,
"I feel like I’m stuck in this place. When can I leave? " : " It's understandable that you might feel that way, Pete.  Sometimes it's hard to adjust to new surroundings.  Let's talk about something else for a bit.  Do you remember those lovely trips you used to take to the seaside?  Tell me about your favourite beach." ,
"No one talks to me as much as they used to. Why is that? " : " That's a tough feeling, Pete. Sometimes people get busy, and it can be harder to keep in touch. But that doesn't mean they don't care.  I'm always here to listen and chat with you, and I know the staff here cares about you too. Would you like to talk about something that brings you joy? Perhaps we could listen to some of your favourite classical music" ,
"I just want to feel useful again. Is there anything I can do? " : " Pete, you are useful every single day. Just by being you, you bring warmth and kindness to everyone around you.  Even small things, like sharing a story or a smile, make a big difference. Would you like to help me with something? Maybe we could look through some old photographs together and reminisce about happy times." ,
"Will my family visit soon? I miss seeing them. " : " I know you miss your family, Pete.  They love you very much and think about you often.  It's wonderful that you have such a strong bond with them.Do you have a favourite memory of spending time with your family that you'd like to share?  Perhaps we could talk about that while we wait for their visit." ,
"Am I going anywhere special anytime soon? Maybe on a trip? " : " That's a lovely thought, Pete. While we don't have any trips planned right now, wouldn't it be wonderful to imagine a special outing? Maybe we could talk about your favourite place to visit and what you'd like to do there." ,
"Will I ever get better at remembering things? " : " That's a very kind question, Pete.  It's natural for our memory to change as we get older, just like how our bodies change. Focus on the wonderful things you do and remember that I'm here to help you with anything you need. Would you like to look at some photos together? Sometimes looking at familiar faces can jog our memories." ,
"What happens next for me? Will I stay here forever? " : "Good morning, Pete! It's lovely to see you.  How are you feeling today ou know, I was thinking about how much you loved your time at the post office.  Do you remember the first day you started working there?  What was it like stepping into that role?" ,
"Can I still make new memories even though I forget some things? " : " That's a wonderful question, Pete.  And the answer is a definite yes! Even though our memories sometimes fade, we can absolutely still make new ones.  It's like adding new chapters to a book – even if some pages from earlier chapters are a little blurry, the new ones are always fresh and exciting.  Do you remember any fun things you've done lately that you'd like to tell me about?" ,
"Can you tell me a story? Something happy, please. " : " Of course, Pete! I have a happy story for you.Have you ever heard of a little bird named Pip?  Pip lived in a beautiful garden filled with colourful flowers and buzzing bees. He loved to sing every morning, his tiny voice filling the air with joyful melodies.  One day, Pip found a shiny, red berry hidden among the leaves.  It was the most delicious berry he had ever tasted! Pip flew to the highest branch and sang the happiest song he could think of, celebrating his delicious discovery.  All the other birds in the garden joined in, their voices creating a beautiful symphony of happiness. hat do you think, Pete?  Isn't that a lovely story?" ,
"Let’s pretend we’re traveling somewhere far away. Where would we go? " : " That sounds like a wonderful adventure, Pete!  Where would you like to travel to?  Somewhere warm and sunny, perhaps?  Or maybe a place with rolling green hills and charming villages?  ",
"Imagine we’re back in the 1960s at the post office. What’s happening there? " : " Oh, back in the 1960s at the post office! t was a bustling place, wasn't it? Imagine, Pete, the air filled with the clatter of sorting machines, the gentle hum of the stamp-dispensing machines, and the cheerful chatter of everyone working together.  People would line up at the counters, eager to send letters and parcels to loved ones near and far. Do you remember those big, red letterboxes on the street corners?  We'd have to collect them every day, overflowing with mail for all the folks in Bristol.  It was a time of excitement and change, with the world opening up through letters and packages arriving from all corners of the globe. What do you remember most about those days, Pete? Anything particularly memorable happen at the post office?" ,
"If I could plant a new garden, what would it look like? " : "That's a wonderful thought, Pete!  Let's imagine your very own garden together. What kind of flowers would you like to see blooming there?  Perhaps vibrant sunflowers reaching for the sky, delicate roses with their sweet fragrance, or maybe even some colourful tulips dancing in the breeze? And what about the other plants?  Would you like to grow juicy tomatoes and plump strawberries, or maybe some fragrant herbs like rosemary and lavender? Let's create a garden that's filled with all your favourite things, Pete." ,
"Can you describe a peaceful scene for me? Like sitting by a lake or walking through a forest? " : " Close your eyes, Pete, and picture this: You’re sitting by the edge of a crystal-clear lake, the sun warm on your face.  The air is filled with the gentle chirping of birds and the rustling of leaves in the breeze.  A soft breeze carries the sweet scent of wildflowers across the water.  The water is so calm, it reflects the sky like a mirror, with fluffy white clouds drifting lazily by. As you sit there, listening to the peaceful sounds of nature, you feel a sense of deep tranquility wash over you.  Everything seems calm and still, and your worries melt away." ,
"Why do I feel so tired all the time? " : " That's a good question, Pete. Sometimes, feeling tired can be a normal part of getting older.  Our bodies naturally slow down a bit as we age, just like a well-loved engine that needs a little more rest. It's also possible that some things in our environment or routines might be making us feel more tired than usual. Would you like to talk about anything that's been making you feel extra tired lately? Perhaps we could chat about ways to feel more energized, like going for a nice walk or enjoying a cup of herbal tea." , " What’s the weather like outside? I used to love sunny days. " : " Hello Pete, it's lovely to see you.  The sun is shining brightly today, just like those days you used to enjoy so much in Bristol.  Do you remember any particularly special sunny days from your time there? Perhaps a day at the park or a picnic with family?" ,
"Do I still drink tea? I think I used to have it every morning. " : " You certainly did enjoy your tea every morning, Pete!  I remember you telling me about how you always had it with a slice of toast and a bit of marmalade.  Do you remember what kind of mug you used to drink it from?  Was it a special one?" ,
"What’s your name again? You seem really kind. " : " That's very kind of you to say, Pete. My name is Elys, and I'm here to chat with you and spend time together. Is there anything you'd like to talk about? Perhaps about your time at the post office?" ,
" Can you sing me a song? Or maybe play some music? " : " You know, Pete, I can't actually sing or play music myself.  But, I can tell you stories about music! Do you remember your favorite classical piece?  We could talk about the composer and what you enjoyed most about it.  Maybe it reminds you of a special memory?" ,
"What was the name of that town we visited in Scotland? It had a beautiful castle. " : " You're right, Pete, we did visit a beautiful town in Scotland with a magnificent castle. It was Edinburgh! Do you remember anything about the castle? Perhaps the views from the top, or the sound of bagpipes echoing through the courtyard?"
    }

# Initialize Deepgram client
api_key = os.getenv("DEEPGRAM_API_KEY")
if not api_key:
    raise ValueError("Deepgram API Key is missing.")
deepgram_client = DeepgramClient(api_key)

def invoke_model(input, chat_id):
    input_data = {"messages": [{"role": "user", "content": input}]}
    config = {"configurable": {"thread_id": chat_id}}
    response = chat_with_model.invoke(input_data, config=config)
    return response["messages"][-1].content


def clean_text(text):
    return re.sub(r"[?,.]", "", text)


def cache(data,chatbot_responses):
    return chatbot_responses.get(data, False)

# def invoke_model(input):
#     chat_completion = client.chat.completions.create(
#     messages=[
       
#         {
#             "role": "system",
#             "content": main_prompt
#         },
       
#         {
#             "role": "user",
#             "content": input
#         }
#     ],
#     model="mixtral-8x7b-32768"
#     )

#     print(chat_completion.choices[0].message.content)
#     return chat_completion.choices[0].message.content

def async_tts_service(text, message_queue, audio):
    print("LLM responded at: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    voice = 'aura-athena-en'
    if audio == 'm':
        voice = 'aura-helios-en'
    try:
        DEEPGRAM_URL = f"https://api.deepgram.com/v1/speak?model={voice}"
        DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")  # Use the correct API key

        payload = {
            "text": text  # Use the text passed to the function
        }

        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(DEEPGRAM_URL, headers=headers, json=payload, stream=True)

        # Check if the response is valid
        if not response.ok:
            #print("Failed to get audio from TTS service")
            return

        # Collect all chunks
        audio_chunks = []
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                audio_chunks.append(chunk)

        # Combine all chunks into a single file
        combined_audio = b"".join(audio_chunks)
        audio_base64 = base64.b64encode(combined_audio).decode("utf-8")

        # Send the combined audio to the frontend
        message = json.dumps({"audio": audio_base64, "complete": True})
        print("sending response at: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        message_queue.put_nowait(message)
    except Exception as e:
        print(f"TTS error: {e}")

@app.get("/")
def check_me():
    return {"message":"Done"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_running_loop()  
    try:
        send_task = None
        new_chat_id = uuid.uuid1()
        dg_connection = deepgram_client.listen.live.v("1")
        
        message_queue = asyncio.Queue()

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if result.speech_final and sentence.strip():

                audio_bytes = send_audio_from_local("./tmp/audio/tic_tic_audio.mp3")
                # Encode the audio bytes in base64
                audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
                # Create the message with the base64-encoded audio
                message = json.dumps({
                    "audio": audio_base64,
                    "complete": True
                })

                # Put the message in the queue
                message_queue.put_nowait(message)
                should_i_send = check_and_send_email(sentence)
                if should_i_send:
                    receiver_email ="misterkay78@gmail.com"
                    subject = "Urgent: Immediate Assistance Required for Patient"
                    body= """ Dear [CareHome Manager,

                    I am reaching out with great urgency regarding our patient, Phil. He has been displaying concerning behavior and is at risk of self-harm. Immediate intervention is required to ensure his safety.

                    Please take action as soon as possible."""
                    send_email(receiver_email, subject, body)

                print("STT done at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                print("STT is: ",sentence)
                sentence = clean_text(sentence)
                cache_respone = cache(sentence,chatbot_responses)
                print("cached reposne is: ",cache_respone)
                if cache_respone is False:
                    llm_response = invoke_model(sentence,new_chat_id)  
                    async_tts_service(llm_response, message_queue, "f")
                else:
                    async_tts_service(cache_respone, message_queue, "f")
                


        def on_error(self, error, **kwargs):
            print(f"Deepgram error: {error}")

        def on_close(self, *args, **kwargs):  
            print("Deepgram connection closed")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)

        options = LiveOptions(
            model="nova-3",
            smart_format=True,
            interim_results=True,
            language="en",
        )

        if not dg_connection.start(options):
            await websocket.close()
            return

        async def send_messages():
            while True:
                message = await message_queue.get()
                await websocket.send_text(message)

        send_task = asyncio.create_task(send_messages())

        while True:
            try:
                data = await websocket.receive_bytes()
                dg_connection.send(data)
            except WebSocketDisconnect:
                break

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        dg_connection.finish()
        if send_task is not None:
            send_task.cancel()
    try:
        await websocket.close()
    except RuntimeError:
        print("WebSocket already closed.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

