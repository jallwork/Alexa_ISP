import random
def freejokes():
    jokes = ["I was awake all night wondering where the sun went, but then it dawned on me",
    "A burger walks into a bar. The bartender says 'Sorry, we don't serve food here'",
    "Once you've seen one shopping center, you've seen the mall.",
    "I didn't like my beard at first. Then it grew on me.",
    "Time flies like an arrow. Fruit flies like a banana.",
    "A backwards poet writes inverse.",
    "To the guy who invented zero: Thanks for nothing!",
    "A man walks into a bar. Ouch! It was an iron bar",
    "What's brown and sticky? A stick."]
    randNo = random.randint(0,len(jokes)-1)
    return jokes[randNo]

def paidjokes():   
    jokes=["I'm reading a book about anti-gravity. I can't put it down.",
    "Do you remember that joke I told you about my spine? It was about a weak back!",
    "I just went to an emotional wedding. Even the cake was in tiers.",
    "When's the best time to go to the dentist? Tooth-hurtie!",
    "Why do seagulls fly over the sea? Because if they flew over the bay, they're bagels!",
    "What do you call a farm that makes bad jokes? Corny!",
    "Why do fish live in salt water? Because pepper makes them sneeze!",
    "What kind of streets do ghosts haunt? Dead ends!",
    "Why do you tell actors to break a leg? Because every play has a cast!",
    "What kind of dogs love car racing? Lap dogs!",
    "What did Winnie the Pooh say to his agent? 'Show me the honey!'",
    "What do you call birds who stick together? Vel-crows.",
    "Today I gave my dead batteries away. They were free of charge.",
    "What do you call it when one cow spies on another? A steak out!"]

    randNo = random.randint(0,len(jokes)-1)
    return jokes[randNo]
