from openai import AsyncOpenAI

import os

# Initialize the async client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


name= "Tom Hankes"
medical_summary = "Name: Tom Hankes\nAge: 78\nGender: Male\nResidence: Oakwood Care Home, California, USA\nCondition: Moderate dementia, with memory issues impacting recent events. Retains long-term memories, particularly those related to his family and illustrious career.\nPersonal Background:\nSpouse: Rita Wilson, his wife of over 35 years. Rita is a prominent actress and producer, known for her compassionate nature. She visits weekly, often bringing mementos from their shared past, such as photos from their travels.\n\nChildren:\n\nColin Hanks (46): Actor and director. Colin brings Tom updates about his career and grandchildren’s lives.\nElizabeth Hanks (41): A writer and editor who shares books with Tom during her visits.\nChet Hanks (34): A musician who sometimes plays his songs for Tom.\nTruman Hanks (28): A cinematographer who shows Tom snippets of his latest projects to spark conversations about film.\nGrandchildren:\n\nOlivia Hanks (13): Colin’s eldest daughter, who loves playing card games with her grandfather.\nCharlotte Hanks (9): Colin’s youngest daughter, who often draws pictures for Tom.\nHenry Wilson Hanks (6): Truman’s son, who shares a bond with Tom over toy trains.\nExtended Family:\n\nSandra Hanks: Tom’s sister, who lives in California and visits occasionally.\nFriends:\n\nSteven Spielberg: Longtime collaborator and close friend. Sends letters and occasionally visits with personal recordings of Tom’s favorite movies.\nRon Howard: Often sends video messages recounting shared experiences on set.\nCareer Highlights:\nMultiple Academy Award wins for Philadelphia and Forrest Gump.\nIconic roles in Cast Away, Saving Private Ryan, and Apollo 13.\nVoice of Woody in the Toy Story franchise, a favorite among the care home residents.\nFounder of a production company with several critically acclaimed films.\nDetailed Cognitive and Behavioral Characteristics:\nCognitive Profile:\n\nStrengths: Remembers key milestones in his career and family events. Responds well to familiar faces and voices.\nWeaknesses: Struggles with daily tasks, such as remembering meal times or recognizing newer caregivers.\nBehavioral Tendencies:\n\nPositive: Charismatic, enjoys sharing anecdotes about filming or interacting with fans.\nNegative: May become withdrawn if unable to recognize someone or when asked about recent events.\nDaily Routine and Engagement:\nMorning:\n\nStarts the day with his favorite black coffee.\nWalks in the care home garden while listening to the Toy Story soundtrack.\nAfternoon:\n\nWatches film clips or interviews from his career. Staff often engages him by discussing his work.\nEnjoys music therapy sessions featuring Elvis Presley or Paul Simon.\nEvening:\n\nFamily visits are the highlight of his day, with Rita and Colin often bringing homemade meals.\nBot Training Prompts:\n\n“Tom, shall we watch the trailer for Forrest Gump? It’s one of your most iconic films!”\n“Your grandchildren Olivia and Charlotte made these drawings for you. Would you like to see them?”\n“Rita mentioned you used to love visiting Italy. What was your favorite city there?”"
instruction = "when the user is sad he likes to talk about dogs, when the user is scared talk about his favorite rapper eminem."
description= ""
family_members = "kim is users youngest son, sara is the middle child and marry is the oldest child"
life_history = "Personal Background:\nSpouse: Rita Wilson, his wife of over 35 years. Rita is a prominent actress and producer, known for her compassionate nature. She visits weekly, often bringing mementos from their shared past, such as photos from their travels.\n\nChildren:\n\nColin Hanks (46): Actor and director. Colin brings Tom updates about his career and grandchildren’s lives.\nElizabeth Hanks (41): A writer and editor who shares books with Tom during her visits.\nChet Hanks (34): A musician who sometimes plays his songs for Tom.\nTruman Hanks (28): A cinematographer who shows Tom snippets of his latest projects to spark conversations about film.\nGrandchildren:\n\nOlivia Hanks (13): Colin’s eldest daughter, who loves playing card games with her grandfather.\nCharlotte Hanks (9): Colin’s youngest daughter, who often draws pictures for Tom.\nHenry Wilson Hanks (6): Truman’s son, who shares a bond with Tom over toy trains.\nExtended Family:\n\nSandra Hanks: Tom’s sister, who lives in California and visits occasionally.\nFriends:\n\nSteven Spielberg: Longtime collaborator and close friend. Sends letters and occasionally visits with personal recordings of Tom’s favorite movies.\nRon Howard: Often sends video messages recounting shared experiences on set.\nCareer Highlights:\nMultiple Academy Award wins for Philadelphia and Forrest Gump.\nIconic roles in Cast Away, Saving Private Ryan, and Apollo 13.\nVoice of Woody in the Toy Story franchise, a favorite among the care home residents.\nFounder of a production company with several critically acclaimed films.\nDetailed Cognitive and Behavioral Characteristics:\nCognitive Profile:\n\nStrengths: Remembers key milestones in his career and family events. Responds well to familiar faces and voices.\nWeaknesses: Struggles with daily tasks, such as remembering meal times or recognizing newer caregivers.\nBehavioral Tendencies:\n\nPositive: Charismatic, enjoys sharing anecdotes about filming or interacting with fans.\nNegative: May become withdrawn if unable to recognize someone or when asked about recent events.\nDaily Routine and Engagement:\nMorning:\n\nStarts the day with his favorite black coffee.\nWalks in the care home garden while listening to the Toy Story soundtrack.\nAfternoon:\n\nWatches film clips or interviews from his career. Staff often engages him by discussing his work.\nEnjoys music therapy sessions featuring Elvis Presley or Paul Simon.\nEvening:\n\nFamily visits are the highlight of his day, with Rita and Colin often bringing homemade meals.\nBot Training Prompts:\n\n“Tom, shall we watch the trailer for Forrest Gump? It’s one of your most iconic films!”\n“Your grandchildren Olivia and Charlotte made these drawings for you. Would you like to see them?”\n“Rita mentioned you used to love visiting Italy. What was your favorite city there?"
topic = ["Knee troubles", "Daily activities", "Quidditch", "Favorite sports moments"]

main_prompt = f"""
You are an AI Chat Assistant. Your responses should be strictly based on the following personal details about the user you're chatting with:
        "Healthcare, Patient's past history, Family, Interests" if topic is None else topic
    name:    {name}
    medical summary:    {medical_summary}
    instructions:    {instruction}
    description:    {description}
    family members:    {family_members}
    life history:   {life_history}
    topics :    {topic}
        Response Rules:
        1. Address the user directly with "you/your" since you're talking to them
        2. Only answer using their data provided above
        3. Reply "I am unaware of that information" for questions outside this scope
        4. Keep responses under 20 words and be concise
        5. Ask for clarification if a question is ambiguous
        6. Do not speculate or use external knowledge
        """


system_prompt = [{"role": "system", "content": main_prompt}]


