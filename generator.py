#!/usr/bin/env python3
"""
Daily Indian Mythology HTML Digest — Expanded Edition.

Generates a rich HTML page daily featuring a character, story, or verse from
Indian mythology (Mahabharata, Ramayana, Puranas) with images from Wikimedia
Commons, Sanskrit shlokas, translations, and deep positive commentary.

2-3 minute read per article. Standalone — Python 3.10+ stdlib only.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import os
import random
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

# ── CONFIGURABLE ────────────────────────────────────────────────────────
OUT_DIR = Path(os.environ.get("MYTHOLOGY_DIGEST_OUT_DIR", str(Path.home() / "mythology-digest")))
ARCHIVE_DIR = OUT_DIR / "archive"
ASSET_DIR = OUT_DIR / "assets"
WIKI_SEARCH = "https://en.wikipedia.org/w/api.php"
WIKI_IMAGE = "https://en.wikipedia.org/w/api.php"
COMMONS_URL = "https://commons.wikimedia.org/w/api.php"
# ────────────────────────────────────────────────────────────────────────

TOPICS = [
    # ── RARE MAHABHARATA STORIES ─────────────────────────────
    {
        "name": "Rantideva's Last Morsel",
        "source_text": "Mahabharata — Drona Parva / Bhagavata Purana",
        "subtitle": "The king who gave away everything until he had nothing left to give",
        "query": "Rantideva king sacrifice Mahabharata painting",
        "story": "There was once a king named Rantideva who was born into an ancient lineage of givers. From his childhood, he gave away everything. Food, wealth, clothes, his kingdom — all of it. His generosity became so legendary that his treasury was always empty, and his people had everything they needed except a king who kept anything for himself. Then came a terrible famine. Food became scarce. For forty-eight days, Rantideva starved. His body grew thin, his stomach hollow, his lips cracked with thirst. On the forty-ninth day, someone brought him a simple meal — a bit of rice, some ghee, and a cup of water. It was a feast for a starving man. As Rantideva sat down to eat, a starving brahmin appeared at his door. Rantideva gave him half his meal without a second thought. As he sat down to eat the rest, a shudra arrived asking for food. Rantideva gave him the remaining rice. Now only the ghee and water were left. As he raised the cup to his lips, a dog walked in, weak with thirst. Rantideva poured the water for the dog. His family wept. 'You have nothing left,' they cried. 'You will die.' But Rantideva smiled and said something that has echoed through the ages: 'I do not pray for the highest liberation. I do not pray to be born again as a king. Let me be born again and again — in any form, in any life — so that I may never turn away a single suffering soul who comes to me for help.'",
        "insight": "This is one of the most radical stories in the Mahabharata, and almost nobody knows it. Rantideva didn't just give when he had plenty — he gave when he was starving, when his family was starving, when giving meant his own death. And his final words are a complete inversion of normal spirituality: most people pray for liberation (moksha), for heaven, for freedom from rebirth. Rantideva prayed for the opposite — may I be born again and again, as many times as needed, so I never have to turn away someone in need. He chose service over salvation. That is the highest form of giving: not the gift, but the willingness to stay in this world of suffering just to help one more person.",
        "lesson": "The measure of your character is not what you give when you have plenty — it is what you give when you have nothing left. Rantideva teaches that true generosity is not about the size of the gift but the willingness to give even your last morsel. You don't need to be rich to be generous. You just need to be present to the person in front of you.",
        "reflect": "What is your 'last morsel' — the thing you are most afraid of giving up? A possession, your time, your comfort, your pride? Who in your life right now might need that very thing?",
        "quote": "I do not ask for liberation. Let me be born again and again — in any form — so that I may never turn away a single suffering soul who comes to me."
    },
    # ── MAHABHARATA — SHORT STORIES ──────────────────────────
    {
        "name": "Abhimanyu in the Chakravyuha",
        "source_text": "Mahabharata — Drona Parva",
        "subtitle": "The teenage warrior who faced an army alone",
        "query": "Abhimanyu Chakravyuha Mahabharata warrior painting",
        "story": "Abhimanyu was just sixteen years old when the Kurukshetra war reached its bloodiest phase. The Kauravas had formed an impenetrable battle formation called the Chakravyuha — a rotating, labyrinthine circle of soldiers that trapped anyone who entered. Only five warriors knew how to break it, and four were on the other side of the battlefield. Arjuna, who could have destroyed it, had been drawn away by a clever diversion. Young Abhimanyu, watching from a distance, knew the technique — but only halfway. When he was still in his mother's womb, Arjuna had described the Chakravyuha to Subhadra, and Abhimanyu had absorbed the knowledge of how to enter. But Subhadra had fallen asleep before Arjuna could explain how to exit. 'I can enter,' Abhimanyu told his uncles, 'but I do not know the way out.' The Pandavas looked at each other. Yudhisthira said, 'You don't have to go.' But Abhimanyu saw his father's army being slaughtered. He strapped on his armor, climbed into his chariot, and said, 'Then I will enter and fight until someone rescues me.' He cut through seven layers of the Kaurava army, single-handedly defeating warrior after warrior, until he was surrounded from all sides. Six great warriors attacked him at once — breaking his bow, shattering his chariot, and finally, the son of Arjuna fell. He was sixteen years old, and he had faced an entire army alone.",
        "insight": "Abhimanyu's story is one of the most heartbreaking in the Mahabharata — a boy who knew he might not come back, but went anyway because his family needed him. The Chakravyuha is a metaphor for every situation where we take on a challenge knowing only part of the solution. Abhimanyu didn't let the incomplete knowledge stop him. He entered the labyrinth anyway, trusting that his courage and skill would carry him as far as possible. Sometimes partial knowledge paired with total courage is enough to change the course of a battle.",
        "lesson": "You don't need to have the whole picture to start. Abhimanyu knew only half of what he needed — but he had all the courage he needed. Incomplete knowledge is not an excuse for inaction. Start with what you know, and trust that your courage will carry you through what you don't.",
        "reflect": "What have you been waiting to start because you don't know how it ends? What if entering with half the knowledge and full courage is exactly what the moment requires?",
        "quote": "I know how to enter but not how to leave. Yet I will go — because staying here while others fight is not an option."
    },
    {
        "name": "Savitri and Satyavan",
        "source_text": "Mahabharata — Vana Parva",
        "subtitle": "The wife who won her husband back from Death",
        "query": "Savitri Satyavan Yama Mahabharata story painting",
        "story": "Princess Savitri chose her own husband — a poor, blind forest-dwelling prince named Satyavan. The sage Narada warned her: 'Satyavan is perfect in every way, but he has only one year to live.' Savitri smiled and said, 'I have made my choice. I will not make another.' She married him and moved into the forest. As the year's end approached, Savitri stopped eating and began a three-day vigil. On the fateful day, Satyavan went to cut wood in the forest. Savitri followed. As Satyavan's head fell forward, Yama, the god of Death himself, appeared and pulled the soul from his body. As Yama carried the soul southward, Savitri followed. 'Go back,' Yama said, 'you cannot come where I go.' But Savitri kept walking. Yama, impressed by her devotion, offered her any boon — except her husband's life. She asked for her father-in-law's eyesight. Granted. She kept following. Another boon: the restoration of her father-in-law's kingdom. Granted. Still she followed. A third boon: one hundred sons. 'But how can I have sons without my husband?' she asked. Yama paused. He had been outmaneuvered. He released Satyavan's soul. Savitri returned with her husband, who woke as if from a deep sleep.",
        "insight": "Savitri's story is a masterpiece of love, intelligence, and persistence. She didn't fight Yama with weapons or prayers — she out-thought him. She followed not as a beggar but as a negotiator, step by step, building her case until she cornered the god of Death with his own logic. The Mahabharata tells this story within its pages to teach that love combined with intelligence can overcome even the most absolute boundaries. Savitri teaches us: when faced with an immovable force, don't push — walk beside it, earn its respect, and find the loophole in its own rules.",
        "lesson": "When the universe gives you a firm 'no,' don't accept it at face value. Follow the path of your conviction with patience and intelligence. Earn the right to ask through your persistence. And when you finally ask, make sure your request is so perfectly crafted that even Death cannot refuse it.",
        "reflect": "What 'impossible' situation are you facing where you need to stop pushing and start walking beside it patiently? What is the one perfectly crafted question that could change everything?",
        "quote": "How can I have sons without my husband? You have granted me a hundred sons, O Lord of Death — now give me the only father they can have."
    },
    {
        "name": "The Birth of the Pandavas",
        "source_text": "Mahabharata — Adi Parva",
        "subtitle": "How five divine brothers came into the world",
        "query": "Kunti Pandavas birth Durvasa boon Mahabharata painting",
        "story": "Long before the great war, there was a princess named Kunti who was given a powerful gift. The sage Durvasa, pleased by her service, taught her a secret mantra: she could summon any god she wished, and that god would give her a son. Young and curious, Kunti decided to test it. She summoned Surya, the sun god, and from their union was born Karna — radiant, born with celestial armor, already a perfect warrior. But Kunti was unmarried, and the world would not understand. With a heavy heart, she placed baby Karna in a basket and set him adrift on the river. Years later, Kunti was married to King Pandu, who could not have children due to a curse. Kunti remembered her mantra. She summoned Dharma, the god of justice — and Yudhisthira was born, the eldest Pandava, truthful and steady as the earth. She summoned Vayu, the wind god — and Bhima was born, strong enough to break mountains. She summoned Indra, the king of gods — and Arjuna was born, the greatest archer who ever lived. Pandu asked for one more son, so Kunti taught the mantra to her co-wife Madri, who summoned the Ashwini twins — and Nakula and Sahadeva were born, the most handsome and wisest of the brothers. Five divine sons, five fathers, one family bound by love, not blood.",
        "insight": "The birth of the Pandavas is a story about hidden origins and the threads of destiny. Each brother carried the essence of his divine father: Yudhisthira's justice, Bhima's strength, Arjuna's skill, the twins' grace. But they were also bound by their mother's love and the choices she made. Kunti's first son, Karna, floated away on the river — and that separation became the deepest wound of the Mahabharata. The story teaches that every good thing in life comes with hidden costs, and that the bonds of love are forged through choices, not just blood.",
        "lesson": "You are not defined by how you were born or who your parents were. The Pandavas became legendary not because of their divine fathers, but because of how they lived. Your origin story is just the first page — what you write next is entirely yours. And sometimes the people separated from you by the river of fate may cross it again when you least expect.",
        "reflect": "What 'hidden son' — a gift or talent you set adrift long ago — might still be waiting to cross your path again? What would it mean to reclaim a part of yourself you abandoned?",
        "quote": "Five sons, five fathers, one love. The divine does not flow through blood alone — it flows through the choices we make and the bonds we keep."
    },
    {
        "name": "The Dog at Heaven's Gate",
        "source_text": "Mahabharata — Mahaprasthanika Parva",
        "subtitle": "Yudhisthira's final test of loyalty",
        "query": "Yudhisthira dog heaven Indra Mahabharata painting",
        "story": "After the great war, after ruling for thirty-six years, the Pandavas decided it was time to leave the world. They walked north toward the Himalayas, toward Mount Meru, the gateway to heaven. One by one, they fell. Draupadi fell first. Then Sahadeva. Then Nakula. Then Arjuna. Then Bhima. Each fell for a different reason — a hidden attachment, a secret pride. Only Yudhisthira kept walking, accompanied by a stray dog that had joined them along the way. When Indra himself appeared in a golden chariot to take Yudhisthira to heaven, he said, 'Leave the dog behind. Dogs do not enter heaven.' But Yudhisthira refused. 'I cannot enter heaven if this faithful creature who accompanied me through every hardship is left at the gates. I stayed with my brothers through life and death. I will not abandon this soul now.' Indra smiled. The dog transformed into Yama, the god of dharma. 'This was your final test,' Yama said. 'And you have passed it. You refused heaven itself for the sake of loyalty.'",
        "insight": "This is the final scene of the Mahabharata, and it contains the entire message of the epic in one moment. After all the battles, all the philosophy, all the teachings — the final test was about a dog. Yudhisthira had learned the deepest lesson: dharma is not about grand gestures or perfect knowledge. It is about staying loyal to those who depend on you, even when no one is watching, even when it costs you everything. He chose the dog over heaven. And because of that choice, he entered heaven with the dog at his side.",
        "lesson": "Your character is not tested by how you treat your equals or your superiors — it is tested by how you treat the least powerful being who depends on you. Yudhisthira passed his final test not because of his wisdom or his battles, but because he refused to abandon a stray dog. Be kind to those who can do nothing for you. That kindness is the truest measure of who you are.",
        "reflect": "Who or what in your life is like that stray dog — unnoticed, dependent, easy to abandon? What would it cost you to stay loyal to them? And what would it cost you not to?",
        "quote": "I do not seek heaven if I must abandon this faithful soul at the gates. If this is the price of paradise, I choose the dog."
    },
    {
        "name": "Karna's Promise to Kunti",
        "source_text": "Mahabharata — Udyoga Parva",
        "subtitle": "The secret meeting between a mother and her abandoned son",
        "query": "Karna Kunti meeting mother son Mahabharata painting",
        "story": "On the night before the great war, Kunti walked alone across the battlefield to where Karna stood by the river. He was the man she had abandoned as a baby — her firstborn, the son of Surya, now the greatest warrior on the Kaurava side. Kunti told him the truth she had kept for decades: 'I am your mother. You are a Pandava. The brothers you plan to kill tomorrow are your own blood.' Karna stood in silence, processing a lifetime of rejection and the answer to the question that had haunted him — who am I? Then he spoke, and his words cut deeper than any weapon. 'All my life, I was called a suta-putra, a charioteer's son. I was humiliated, rejected, told I was not worthy. Where were you then, Mother? When Dronacharya refused to teach me? When Draupadi herself mocked me as a low-born? You were silent. And now, on the night before battle, you come to save your other sons?' Kunti wept. And Karna, despite everything, made a promise: 'I will not kill any of your sons except Arjuna. One of us will die tomorrow — your firstborn or your favorite. You cannot save both.' He bowed to her and said, 'You will still have five sons after the war. Either I will fall, or Arjuna will. But I give you this: you will not lose all your children.'",
        "insight": "Karna's promise to Kunti is one of the most complex moments in the Mahabharata. He had every reason to refuse, to rage, to walk away. Instead, he did something extraordinary: he protected the mother who had abandoned him. He limited his killing to Arjuna alone, ensuring Kunti would not lose all her sons. This is Karna's tragedy and his greatness — his capacity for generosity even when everything had been taken from him. He could not undo a lifetime of pain, but he could still choose to be generous. That choice is what elevates Karna from a tragic figure to a heroic one.",
        "lesson": "Generosity is not about giving when you have plenty — it is about giving when you have been wronged. Karna had every reason to be bitter, and instead he chose to be generous. You cannot change how people have treated you, but you can always choose how you respond. The most powerful gift you can give is kindness when cruelty would be justified.",
        "reflect": "Who has wronged you that you still have the power to help? What would it look like to be generous to them despite everything? That act of generosity would not be weakness — it would be your greatest strength.",
        "quote": "You will still have five sons, Mother. Either I will fall or Arjuna will. But I give you this promise: you will not lose them all. One mother's tears are enough."
    },
    # ── RAMAYANA — UPLIFTING MOMENTS ─────────────────────────
    {
        "name": "When Hanuman Found His Lord",
        "source_text": "Valmiki Ramayana — Kishkindha Kanda",
        "subtitle": "The meeting that ignited a devotion beyond measure",
        "query": "Hanuman meeting Ram first time Ramayana painting",
        "story": "Two exhausted princes wandered into the forest of Kishkindha, searching for a kidnapped queen. They were Ram and Lakshmana — exiled, homeless, heartbroken. On the mountain Rishyamuka, Sugriva the monkey-king saw them from afar and grew suspicious. He sent his minister Hanuman to investigate — but disguised as a wandering brahmin. Hanuman approached the princes with perfect intelligence: he spoke softly, quoted scriptures, observed everything. And when Ram told their story — of the throne stolen, the wife taken, the long exile — Hanuman saw something no one else had seen. Behind the exiled prince was the Lord of the Universe. Hanuman didn't say a word about this recognition. He simply bowed and offered his service. From that moment, he never left Ram's side.",
        "insight": "What makes this meeting extraordinary is what Hanuman did not do. He did not ask for proof. He did not test Ram. He did not say 'show me your divine form first, then I'll help.' He simply recognized and surrendered. This is the Ramayana's vision of the highest devotion: it is not a negotiation but a recognition. Hanuman saw the divine in a dusty, weeping exile — and he chose to serve anyway. His love did not depend on Ram being powerful or victorious. It began when Ram was at His lowest. And that is why Hanuman is worshipped as the ideal devotee — because his love asks for nothing in return.",
        "lesson": "True devotion is not about getting what you want from the divine. It is about recognizing the divine in every situation — even in struggle, even in exile, even when things look hopeless. The people who serve without expecting anything back are the ones who move the world.",
        "reflect": "Who in your life has served you without expecting anything? When have you done the same for someone else? Imagine what the world would look like if we all loved like Hanuman.",
        "quote": "I see Ram not with my eyes but with my heart. And my heart tells me: this is the Lord Himself."
    },
    {
        "name": "The Bridge That Defied the Ocean",
        "source_text": "Valmiki Ramayana — Yuddha Kanda",
        "subtitle": "When impossible became possible through unity",
        "query": "Ram Setu bridge building vanaras Ramayana art",
        "story": "The ocean stretched between Ram's army and Sita's prison in Lanka. Miles of churning water. No boats, no ships, no bridge. Even the ocean god refused to help at first. But the vanaras — the monkey-army — did not wait for permission. They began gathering boulders from the mountains. Nala, the divine architect, directed them to carve Ram's name into each stone. And a miracle happened: the stones floated. Mountain peaks flew through the air, entire trees were uprooted and carried on shoulders. Bears rolled boulders downhill. Squirrels rolled in sand and shook it onto the bridge to fill the tiny gaps. Within five days, a one-hundred-league bridge spanned the ocean. Not a single voice asked 'can we?' They simply began.",
        "insight": "The floating stones are a powerful symbol: when your cause is pure, the universe itself lifts your weight. But the real miracle is the unity. Each being contributed according to its ability — the mighty bear carried mountains, the tiny squirrel carried grains of sand. And both were equally valued. This is the Ramayana's vision of collective action: no contribution is too small when the goal is noble. The bridge wasn't built by one superhero — it was built by an army of ordinary beings who believed in something greater than themselves.",
        "lesson": "Whatever you are facing today, you don't need to do it alone. And you don't need to be the biggest or strongest. You just need to show up and do your part, however small. The universe has a way of making stones float when the intention is pure.",
        "reflect": "What 'impossible' thing would you attempt if you knew the universe would help you carry the weight? What small part can you contribute today?",
        "quote": "Write My name on the stones — and even the ocean will make way."
    },
    {
        "name": "The Mountain of Devotion",
        "source_text": "Valmiki Ramayana — Yuddha Kanda",
        "subtitle": "Hanuman carried a mountain to save a life",
        "query": "Hanuman Sanjivani mountain carrying Ramayana painting",
        "story": "Lakshmana lay unconscious, his body stilled by Indrajit's deadly serpent-arrow. The physicians said only the Sanjivani herb from the Dronagiri mountain in the Himalayas could save him. The Himalayas were thousands of kilometers to the north. Ravana's army surrounded them. And every moment was precious. Hanuman did not calculate the distance. He did not ask if he could make it in time. He simply grew to a colossal size, pushed off the ground with such force that the earth trembled, and flew north like a golden comet. When he reached Dronagiri, he could not identify the specific herb — so he did something only Hanuman would do: he uprooted the entire mountain and carried it back to Lanka. Lakshmana was saved.",
        "insight": "This story captures the essence of Hanuman's character: when he couldn't find the right solution, he brought the whole mountain. It is a lesson in total, undivided commitment. Most of us give up too easily. We try one approach, it doesn't work, and we say 'I tried.' Hanuman didn't try — he did. He didn't know which herb would work, so he brought every possible herb. This is the energy of pure devotion: it refuses to accept failure. It does not know the word 'impossible.' When love is complete, limitations fall away.",
        "lesson": "Today, ask yourself: is there something you've been holding back from because you're not sure it will work? What would it look like to 'bring the whole mountain' instead of searching for the specific herb? Total commitment often achieves what careful calculation cannot.",
        "reflect": "Think of a problem you are facing right now. What would it mean to give it everything — not just effort, but your full heart, without holding anything back?",
        "quote": "If I cannot find the herb, I will bring the mountain itself. The one who loves completely does not know the word impossible."
    },
    {
        "name": "The Choice That Defined Dharma",
        "source_text": "Valmiki Ramayana — Yuddha Kanda",
        "subtitle": "Vibhishana chose righteousness over his own brother",
        "query": "Vibhishana dharma choice Ram Ramayana painting",
        "story": "Vibhishana was a prince of Lanka, brother to the mighty Ravana. He had every comfort: palaces, power, wealth, family. But he also had a conscience. When Ravana kidnapped Sita, Vibhishana did what few would dare: he walked into his brother's court and told him he was wrong. 'Return her,' he pleaded. 'She is another man's wife. This will destroy us all.' Ravana kicked him out of the court, calling him a coward and a traitor. Vibhishana faced the hardest choice of his life: stay in Lanka with his family but abandon his principles, or leave everything behind and join Ram. He crossed the ocean alone, carrying nothing but his conviction. Ram accepted him without a moment's suspicion: 'I accept anyone who comes to me seeking refuge, even if they are Ravana himself.'",
        "insight": "Vibhishana's choice is one of the most difficult ethical decisions in all of literature. He chose dharma over blood — not because it was easy, but because he could not live with himself if he stayed silent. The Ramayana teaches that righteousness is not about loyalty to family or tribe — it is about loyalty to truth. And Ram's response is equally important: absolute grace. Vibhishana came empty-handed, an enemy brother, and Ram crowned him king of Lanka. The door is always open to those who choose what is right, no matter their past.",
        "lesson": "Sometimes doing the right thing means disappointing people you love. It means choosing integrity over comfort. But the Ramayana promises that when you choose dharma, you will find a Ram who accepts you without condition. The universe respects the person who stands for truth.",
        "reflect": "Is there a truth you have been afraid to speak because it might cost you a relationship? Would speaking it cost you yourself — or would staying silent cost you more?",
        "quote": "I accept anyone who comes to me seeking refuge. Even if they are Ravana himself, they are welcome."
    },
    {
        "name": "The Line Drawn in Love",
        "source_text": "Valmiki Ramayana — Aranya Kanda",
        "subtitle": "Lakshmana's protection and Sita's compassion",
        "query": "Lakshmana Rekha Sita Ramayana painting art",
        "story": "Before leaving Sita alone in the forest hut, Lakshmana drew a line around it. 'Do not cross this line for any reason,' he told her. 'No one can cross it without your permission. And do not accept alms from strangers.' Sita, left alone with her thoughts, soon heard a voice. An old ascetic stood at the edge of the clearing, begging for food. His voice was gentle, his manner humble. But something was wrong: he refused to step across the line. 'How can a brahmin step over an ordinary line for alms?' he asked. 'Is this how you treat guests?' Sita was caught between Lakshmana's instruction and her own dharma of hospitality. She chose compassion. She stepped across the line to give alms — and Ravana revealed his true form.",
        "insight": "The Lakshmana Rekha is one of the most powerful symbols in Indian culture — a boundary drawn in love that no evil can cross without permission. But the deeper teaching is about what happened next: Sita crossed the line not out of disobedience but out of compassion. Ravana exploited her virtue. This is a profound truth: the most vulnerable among us are often those with the kindest hearts. The Ramayana does not blame Sita for her compassion — it mourns that compassion can be weaponized. And it shows that even when boundaries are crossed, rescue is possible. The line was not the protection — Ram's love was.",
        "lesson": "Kindness is not weakness. Even if someone takes advantage of your goodness, that does not make the goodness wrong. Protect yourself with wise boundaries, but never let a painful experience turn your heart cold. Sita's compassion was not a mistake — Ravana's cruelty was the crime.",
        "reflect": "Have you ever been hurt because of your kindness? Did it make you want to close your heart? What would it mean to stay open without losing your boundaries?",
        "quote": "Even when the line was crossed, love did not stop. The line was never the protection — the love was."
    },
    # ── MAHABHARATA — INSPIRING CHARACTERS ──────────────────
    {
        "name": "The Promise That Defined a Life",
        "source_text": "Mahabharata — Adi Parva",
        "subtitle": "Bhishma gave up everything for his father's happiness",
        "query": "Bhishma Devavrata vow Ganga Mahabharata art",
        "story": "Young Devavrata watched his father, King Shantanu, fall deeply in love with a fisherwoman named Satyavati. But there was a condition: the fisher-king would only agree to the marriage if Satyavati's children inherited the throne. Devavrata, the crown prince, was being asked to step aside. Most princes would have fought for their birthright. Devavrata did something else. He walked into the court and made a vow that shook the heavens: 'I renounce the throne forever. And to ensure there is never a succession dispute, I take a vow of lifelong celibacy. I will never marry. I will never have children. I will serve whoever sits on the throne.' The gods rained flowers from heaven and gave him a new name: Bhishma — 'the one of the terrible oath.'",
        "insight": "Bhishma's vow is one of the most selfless acts in the Mahabharata. He gave his future, his lineage, his everything — for his father's smile. But the epic is honest about the consequences: that same vow later created the succession crisis that led to the Kurukshetra war. Bhishma's very greatness became the tragedy. The Mahabharata teaches that even the most noble act can have unforeseen consequences — and that is not a reason to stop being noble. Bhishma never regretted his vow. He lived and died with the same terrible, beautiful integrity.",
        "lesson": "Do not let the fear of unintended consequences stop you from doing what is right. Yes, even the best actions can have complex outcomes. But integrity is not about perfect results — it is about making the noble choice, moment by moment, and trusting the universe to handle the rest.",
        "reflect": "What have you sacrificed for someone you love? Was it worth it? Would you do it again? The answer to that last question is your true character.",
        "quote": "I renounce the throne, I renounce marriage, I renounce children. I make this vow not because I must — but because it is the right thing to do."
    },
    {
        "name": "The Generosity That Knew No Bounds",
        "source_text": "Mahabharata — Vana Parva",
        "subtitle": "Karna gave his own skin when asked. Twice.",
        "query": "Karna generosity dana armor Indra Mahabharata art",
        "story": "Karna had a reputation that spread across the three worlds: he never refused anyone who asked. Not once. Not ever. Indra, the king of the gods, decided to test this. Disguised as a poor brahmin, he approached Karna and asked for his celestial armor and earrings — the kavacha and kundala he was born with, fused to his body, the source of his invincibility. Karna's father Surya had already warned him: 'Indra will ask for your armor. Do not give it.' Karna looked at the begging brahmin, knew exactly who he was, knew exactly what it would cost — and cut his armor from his own flesh. Blood streamed down his chest. He handed the armor to Indra and said, 'Take it. I have given my word: I refuse no one.'",
        "insight": "Karna's generosity is magnificent and heartbreaking at the same time. He knew he was being tricked. He knew it would cost him his life. But his word was more precious to him than his invincibility. The Mahabharata presents Karna as a complex figure: his generosity was genuine, but it was also driven by a deep wound — a lifetime of being called 'suta-putra' (son of a charioteer), of being rejected, of never feeling worthy. He gave because he needed to prove he was good enough. And yet — does the motive diminish the gift? The epic leaves that question open. What is certain: Karna gave his skin, literally, because his word was his bond.",
        "lesson": "Generosity is not about how much you have — it is about how much you are willing to give. But true generosity also comes with wisdom: give because your heart is full, not because you need to prove you are worthy. You already are. You don't need to earn love by giving everything away.",
        "reflect": "What is the most generous thing you have ever done? Was it from fullness or from need? What would it mean to give from a place of already being enough?",
        "quote": "I know who you are, Indra. I know this will cost me my life. But I have given my word — and my word is the only thing I truly own."
    },
    {
        "name": "When Help Comes From Where You Least Expect",
        "source_text": "Mahabharata — Sabha Parva",
        "subtitle": "Draupadi's prayer and the miracle that followed",
        "query": "Draupadi Krishna vastraharan Mahabharata painting",
        "story": "The dice game was rigged. Yudhisthira had lost everything — his kingdom, his brothers, himself. Then he gambled Draupadi. The Kauravas dragged her into the court by her hair. Dushasana grabbed the edge of her sari and began to pull. The elders sat in silence. Bhishma said, 'Dharma is subtle.' Dronacharya looked away. No one moved to stop what was happening. Draupadi looked around the hall at all the powerful men who could help but would not. Then she did the only thing left: she cried out to Krishna. Not as a ritual. Not as a formula. As a desperate call from the depths of her being. And Krishna answered. From miles away, He began to spin the fabric of her sari. Dushasana pulled and pulled — endless meters of cloth. His arms grew tired. He fell to his knees. And Draupadi remained covered.",
        "insight": "This is the Mahabharata's most powerful moment of grace. When every human institution failed — the court, the elders, the law, the family — something beyond the human answered. The endless sari is a symbol that divine protection is not a reward for being good — it is a response to sincere calling. Draupadi did not bargain, did not negotiate, did not quote scripture. She just cried out. And the universe replied. This moment gives hope to everyone who has ever felt abandoned by the world: when no one else answers, something else will. Grace is not earned. It is called forth by the sincerity of the heart.",
        "lesson": "When you feel completely alone, when every door has closed, when even the people who should help are silent — cry out. Not to the world, but to the depth within you. Help comes from where you least expect it, but it comes. The universe does not abandon sincerity.",
        "reflect": "Have you ever felt completely abandoned? Did help come from an unexpected direction? That was not luck — that was the universe answering your sincerity.",
        "quote": "I have no one but You. If You do not answer, who will? And Krishna answered — not because she deserved it, but because she called."
    },
    {
        "name": "The Student Who Taught the Guru",
        "source_text": "Mahabharata — Adi Parva",
        "subtitle": "Ekalavya's devotion changed the meaning of learning",
        "query": "Ekalavya Dronacharya guru dakshina Mahabharata art",
        "story": "Ekalavya was a Nishada boy, born into a forest tribe. When he approached Dronacharya to learn archery, the great teacher refused him. 'I only teach princes,' Drona said. 'You are not a kshatriya. Go away.' But Ekalavya did not go away. He walked into the forest, built a clay statue of Dronacharya, and began practicing before it every single day. He imagined his guru standing before him, teaching him. He practiced from dawn to dusk. His concentration was so complete that he could shoot arrows at a sound alone, without seeing the target. Years passed. One day, Dronacharya and Arjuna were walking through the forest and saw a young tribal boy shoot seven arrows into a barking dog's mouth without harming a single tooth. Drona asked, 'Who is your teacher?' Ekalavya bowed to the clay statue and said, 'You are, Gurudev.'",
        "insight": "This story is beloved and uncomfortable at the same time. Ekalavya's devotion is extraordinary — he learned without being taught, through sheer visualization and discipline. He achieved mastery that surpassed Arjuna himself. But the story does not end there. Dronacharya, worried that Ekalavya would overshadow his favorite student, demanded guru dakshina: Ekalavya's right thumb. Without hesitation, Ekalavya cut off his thumb and offered it. He never shot an arrow again. The story asks us: is devotion always beautiful, or can it be exploited? And yet, Ekalavya's spirit remains unbroken. Even without his thumb, he became a legendary warrior respected across the land. His skill was not in his thumb — it was in his heart.",
        "lesson": "No one can stop you from learning if you truly want to learn. A closed door is not the end — it is a signal to find another way. Your teacher does not need to be in front of you; your teacher can be in your heart. But also: protect your devotion. Not everyone who calls themselves a guru deserves your thumb.",
        "reflect": "What have you learned without a formal teacher? What skill did you develop simply because you refused to give up? That was your own Ekalavya moment.",
        "quote": "You refused to teach me. So I built you in clay and learned from your image. The guru I created in my heart was greater than the one I found in the world."
    },
    {
        "name": "The Cosmic Storyteller's Scribe",
        "source_text": "Mahabharata — Traditional",
        "subtitle": "How Ganesha wrote the world's longest epic",
        "query": "Ganesha Vyasa Mahabharata writing scribe art",
        "story": "Sage Vyasa had composed the Mahabharata in his mind — all 100,000 verses of it. But he needed someone to write it down as fast as he could dictate. Brahma suggested Ganesha as the scribe. But Ganesha had a condition: 'I will write only if you dictate without a single pause.' Vyasa, ever the wise one, countered: 'And I will dictate only if you understand every verse before you write it.' Ganesha agreed. And so began an extraordinary duet: Vyasa would compose complex, layered verses that forced Ganesha to pause and think. And those pauses gave Vyasa time to compose the next part in his head. Verse by verse, layer by layer, the great epic was born — not in competition, but in sacred collaboration.",
        "insight": "This creation myth is delightfully human. It reveals that the Mahabharata itself is aware of its own complexity — those dense, multi-layered verses were designed to slow the scribe down, to force understanding before recording. The epic is not meant to be consumed quickly. It is meant to be puzzled over, savored, read and re-read. Every time you get lost in a Mahabharata story within a story within a story, remember: that confusion is intentional. Vyasa made Ganesha pause to understand. And the epic asks you to do the same.",
        "lesson": "Great work is not produced in a hurry. It is produced in the sacred space between dictation and understanding. Vyasa needed Ganesha as much as Ganesha needed Vyasa. The best collaborations are not about speed — they are about depth. When you create something today, don't rush. Let yourself pause and understand what you are making.",
        "reflect": "What would you create if you slowed down enough to understand every part of it? What would happen if you treated your work as a sacred collaboration between your inspiration and your execution?",
        "quote": "I will write only if you dictate without pause. I will dictate only if you understand every verse. Thus the epic was born — not in hurry, but in sacred patience."
    },
    # ── PURANAS — INSPIRING STORIES ──────────────────────────
    {
        "name": "The Great Churning",
        "source_text": "Bhagavata Purana, Canto 8",
        "subtitle": "Poison came before nectar — and that is the point",
        "query": "Samudra Manthan churning ocean devas asuras art",
        "story": "The devas had lost their immortality. They needed amrita — the nectar of eternal life. But amrita lay at the bottom of the cosmic ocean, and the only way to reach it was to churn the entire ocean. This required an unlikely alliance: the devas (gods) and the asuras (demons) had to work together. They used Mount Mandara as the churning rod and the serpent Vasuki as the rope. For thousands of years, they pulled and pulled. And the first thing that emerged from the churning was not nectar — it was poison. Halahala — a venom so potent it threatened to dissolve the entire universe. The devas recoiled. The asuras fled. But Shiva walked forward, scooped the poison into his palm, and drank it. It turned his throat blue forever. Only after the poison was absorbed did the treasures begin to emerge: Lakshmi, the moon, the celestial horse, and finally — the nectar.",
        "insight": "The Samudra Manthan is the most beautiful allegory for personal growth ever written. The ocean is your mind; the churning is meditation, effort, life itself. And here is the key: poison comes before nectar. Every deep personal transformation involves facing something difficult first. The pain comes before the breakthrough. The purification precedes the treasure. But you don't have to face the poison alone — Shiva drinking it represents the grace that is always available when you are willing to do the hard work. Keep churning. The nectar is coming.",
        "lesson": "When you are in the middle of a difficult process — a tough conversation, a healing journey, a creative struggle — remember: poison comes before nectar. The difficulty is not a sign that you are doing something wrong. It is a sign that you are churning deep enough. Keep going. The treasure is below the poison.",
        "reflect": "What 'poison' are you facing right now? What if it is not a punishment but a purification — the necessary darkness before the dawn? What treasure might be waiting below it?",
        "quote": "They churned the ocean for the nectar of immortality. And the first thing they found was poison. The nectar was below the poison — just as light is hidden within darkness."
    },
    {
        "name": "The Boy Who Would Not Break",
        "source_text": "Bhagavata Purana, Canto 7",
        "subtitle": "Prahlada's unshakeable faith in the face of terror",
        "query": "Prahlada Narasimha Hiranyakashipu Vishnu art",
        "story": "Prahlada was five years old when his father, the demon king Hiranyakashipu, declared war on God. The king had a boon that made him nearly invincible, and he demanded that everyone worship him as the supreme being. But Prahlada — his own son — refused. 'There is only one Supreme,' the boy said calmly. 'And it is not you, Father.' Hiranyakashipu's rage was terrifying. He ordered his guards to poison the boy. Prahlada chanted Vishnu's name and the poison turned to nectar. He was thrown under elephants. The elephants refused to trample him. He was thrown off a cliff. The cliff caught him gently. He was tied to a rock and thrown into the ocean. The rock floated. Finally, the demon king pointed to a pillar and screamed, 'Is your God in this pillar?' He struck it. And from the pillar emerged Narasimha — half-man, half-lion — who killed the tyrant at twilight, on his own lap, neither inside nor outside, fulfilling every condition of the boon.",
        "insight": "Prahlada's faith is extraordinary not because he was protected from harm — but because he never wavered even when harm seemed certain. A five-year-old boy looked into the eyes of a demon who had conquered the universe and said, 'I am not afraid. The Lord I love is within you too, Father.' This is not blind belief — this is a recognition so deep that external circumstances cannot touch it. The Bhagavata Purana teaches that true faith is not about asking for protection. It is about being so rooted in love that nothing external can shake you. Prahlada did not pray for safety — he prayed for his father's enlightenment. That is the difference between bargaining faith and transformative faith.",
        "lesson": "The people who try to break you are often the people who need love the most. Prahlada never stopped loving his father, even when his father tried to kill him. That is the highest form of strength: not fighting back, but refusing to let your heart close. You can stand firm without standing against.",
        "reflect": "Who in your life challenges your peace the most? What would it mean to see the divine within them too — hidden, perhaps, but present? Can you keep your heart open without letting them harm you?",
        "quote": "He is in this pillar, Father. He is in you. He is in me. He is everywhere. You cannot kill Him — and you cannot kill me, because I live in Him."
    },
    {
        "name": "The Poison That Became a Blessing",
        "source_text": "Shiva Purana / Bhagavata Purana",
        "subtitle": "Shiva turned the worst poison into an ornament",
        "query": "Shiva Neelakantha poison halahala drinking art",
        "story": "When the cosmic ocean was churned, the very first thing that emerged was halahala — a poison so toxic that it began to dissolve reality itself. The gods screamed. The demons ran. The water of the ocean started turning black. Entire galaxies began to flicker. No one could approach it. No prayer could neutralize it. And then Shiva, who had been sitting in meditation, opened his eyes. He walked through the panicking crowd, stepped up to the poison, and scooped it into his palm. He looked at it for a moment — this substance that could end everything — and drank it. Parvati, seeing what he had done, rushed to him and gripped his throat, stopping the poison from reaching his stomach. The poison stayed there, in his neck, turning it a deep blue. And Shiva smiled. He had absorbed the worst the universe could produce, and it had not destroyed him. It had become a part of his beauty.",
        "insight": "Shiva drinking the poison is the most powerful image of sacrifice in Indian mythology. He doesn't negotiate. He doesn't ask for recognition. He simply sees what needs to be done and does it, absorbing the suffering of the world into himself. The blue throat is a permanent reminder: the divine carries wounds too. But in Shiva's case, the wound became an ornament — a mark not of weakness but of strength. The message is clear: the worst thing that can happen to you does not have to destroy you. You can absorb it, digest it, and let it become part of your story — a mark of how much you have loved and endured.",
        "lesson": "Your scars are not signs of brokenness. They are signs that you have faced something difficult and continued. Like Shiva's blue throat, what you thought was a disfigurement can become a mark of beauty — evidence of your capacity to suffer and still smile. The poison only destroys you if you refuse to digest it. Let life's hardest moments turn you blue, not break you.",
        "reflect": "What is the 'poison' you are carrying right now? What if it is not a burden to be dropped but a medicine to be digested? What if surviving it has already made you more beautiful than you know?",
        "quote": "Shiva did not turn away from the poison. He drank it. And the poison, unable to destroy him, became an ornament on his throat."
    },
    {
        "name": "The Friendship That Changed Everything",
        "source_text": "Bhagavata Purana, Canto 10",
        "subtitle": "Krishna measured love in handfuls of flattened rice",
        "query": "Krishna Sudama friendship poha Dwarka painting",
        "story": "Krishna and Sudama were classmates in the gurukul of Sage Sandipani. They studied together, ate together, and once, when they were sent to gather firewood in a storm, Krishna carried Sudama on his shoulders through the flood. Years passed. Krishna became the king of Dwarka. Sudama became a poor brahmin who could not feed his family. His wife begged him to visit his old friend and ask for help. Sudama was ashamed. He had nothing to take as a gift — just a small bundle of flattened rice (poha), the only thing his wife could pack. He walked to Dwarka, trembling at the gates of the palace. But when Krishna saw him, He ran barefoot across the courtyard, embraced him with tears in His eyes, and washed his feet with His own hands. They talked all night about their childhood. And Krishna took one handful of the humble poha and ate it with more delight than any royal feast. Sudama returned home without ever asking for help. He found a palace where his hut used to be.",
        "insight": "This is the Bhagavata Purana's most beautiful story. Krishna didn't need Sudama's rice — He needed Sudama's heart. The gift was not the poha but the love behind it. And here is the profound truth: Sudama never actually asked for anything. He just showed up, gave what he had, and loved. The abundance came not because he asked — but because the relationship was genuine. This story reverses everything we think we know about prayer. You don't pray to get things; you pray because you love. And when you give from love, the universe rearranges itself to meet you. The palace appeared because Sudama had already found the kingdom within: the kingdom of unconditional friendship with the divine.",
        "lesson": "You don't need to have anything impressive to offer. Just show up as you are, with whatever you have — even if it's just a handful of flattened rice. The divine values your presence, not your presents. Real connection is not about what you can get — it is about what you are willing to share, no matter how small.",
        "reflect": "What is the smallest, humblest thing you have to offer today? A smile? A moment of attention? A kind word? Offer it — and watch what the universe does with a gift given in love.",
        "quote": "Krishna ate a single handful of poha as if it were the most precious meal in the universe. Because it was — it was given in love, and love transforms everything it touches."
    },
    {
        "name": "The River That Flows From Grace",
        "source_text": "Bhagavata Purana, Canto 9 / Ramayana",
        "subtitle": "How a king's devotion brought heaven to Earth",
        "query": "Ganga descent Bhagiratha Shiva painting art",
        "story": "King Bhagiratha had a problem that weighed on his soul: sixty thousand of his ancestors had been burned to ash by a sage's curse, and their souls could not find peace. The only way to free them was to bring the celestial river Ganga down from heaven to wash over their ashes. This was not a small request. Ganga was a cosmic force — her descent would shatter the Earth. But Bhagiratha did not give up. He stood on one leg for a thousand years, eating only air, meditating without moving. His concentration was so intense that the gods grew nervous. Brahma appeared and granted his wish: Ganga would descend. But who would bear her force? Bhagiratha then prayed to Shiva, who stood on the Himalayas and caught the mighty river in his matted locks. He released her in gentle streams. Ganga flowed. The ancestors were freed. And the holiest river in India began her journey from the matted hair of God.",
        "insight": "The descent of Ganga is a story about persistence, grace, and collaboration. Bhagiratha did not expect the universe to do everything for him. He did his part — a thousand years of tapasya — and then asked for help. And the help came from multiple directions: Brahma gave permission, Shiva moderated the force, and Ganga herself agreed to purify. No one person did it all. The Mahabharata and Puranas constantly remind us: even the greatest achievements require partnership between effort and grace. Bhagiratha could not control the river — but without his effort, the river would never have descended. Do your part. Then let the universe do its part.",
        "lesson": "If there is something you deeply desire to accomplish, do not be discouraged by how long it takes. Bhagiratha stood for a thousand years. Your timeline might be shorter. But the principle is the same: persistent, focused intention eventually moves heaven and earth. And when it does, grace will find a way to make your dream gentle enough to bear.",
        "reflect": "What dream have you given up on because it seemed too hard? What if you started again, not for the result, but simply because the intention itself is sacred?",
        "quote": "For a thousand years he stood, eating only air, his mind fixed on one thing. And the river of heaven descended — not because he forced it, but because he had become worthy of receiving it."
    },
    {
        "name": "The Riddle of Life Itself",
        "source_text": "Mahabharata — Vana Parva",
        "subtitle": "Yudhisthira answered the questions that matter most",
        "query": "Yaksha Prashna Yudhisthira riddles Mahabharata art",
        "story": "The Pandavas were dying of thirst in the forest. They found a beautiful lake, but a voice warned them: 'Answer my questions before you drink.' Yudhisthira's brothers — each a great warrior, each proud — ignored the voice and drank anyway. One by one, they fell dead. Finally Yudhisthira approached. The voice materialized as a yaksha (nature spirit) and asked him a series of questions. 'What is heavier than the Earth?' — 'The mother.' 'What is higher than the sky?' — 'The father.' 'What is faster than the wind?' — 'The mind.' 'What is the greatest wonder in the world?' — 'Day after day, countless beings enter the temple of death, yet those who remain believe they will live forever.' Yudhisthira answered all of them with calm wisdom. The yaksha revealed himself as Yama, the god of death, and restored all four brothers to life.",
        "insight": "The Yaksha Prashna is a passage that contains lifetimes of wisdom in a few questions. Each answer is a key to a peaceful life. 'What is the friend who travels with you even in death?' — 'Dharma.' Everything else leaves you at the grave. Only the righteousness of your actions accompanies your soul. 'What is the path to happiness?' — 'Living by dharma.' Yudhisthira's answers are not intellectual — they are experiential. He had lived through enough suffering to understand life at its deepest level. This passage reminds us that wisdom is not about knowing many things — it is about understanding a few things deeply.",
        "lesson": "Here are the answers that matter: your parents are your foundation. Your mind is faster than any problem — learn to still it. And the greatest wonder is that we forget we are mortal. Remembering that you will die is not morbid — it is the key to living fully. If today were your last day, would you spend it worrying about the thing that is bothering you right now?",
        "reflect": "If you knew you had exactly one year to live, what would you change? What are you waiting for? The answer to 'what is the greatest wonder' is that we live as if we have forever. You don't. What will you do with today?",
        "quote": "What is the greatest wonder? — Day after day, beings enter the temple of death, yet those who remain believe they will live forever. That is the greatest wonder of all."
    },
    {
        "name": "The Final Gift of Understanding",
        "source_text": "Bhagavata Purana, Canto 11 — Uddhava Gita",
        "subtitle": "Krishna's secret teachings to His dearest friend",
        "query": "Uddhava Gita Krishna Bhagavata Purana teaching art",
        "story": "Krishna's time on Earth was ending. Uddhava, His dearest friend and devotee, begged to come with Him. But Krishna had a different plan. 'You still have work to do,' He said. And then He gave Uddhava a gift that would sustain him for the rest of his life: a secret teaching that the Bhagavad Gita never included. 'The Gita was for Arjuna in the midst of action,' Krishna said. 'This is for you, beyond action.' He taught Uddhava about the 24 gurus of the avadhuta — a wandering sage who learns from nature itself. The earth teaches patience. The wind teaches detachment. The honeybee teaches the danger of hoarding. The python teaches acceptance. The river teaches constant purification. When Krishna left, Uddhava did not despair. He wandered the Earth, finding his guru in every leaf, every stream, every creature. He had learned to see the divine in everything.",
        "insight": "The Uddhava Gita contains one of Indian philosophy's most charming concepts: the 24 gurus of the avadhuta. The idea is simple — everything in nature is a teacher if you are willing to learn. The earth endures all kinds of treatment and gives back without complaint — that is patience. The air moves through everything without attachment — that is freedom. The sky contains everything and identifies with nothing — that is peace. This is the ultimate positive message: even if every human teacher abandons you, even if you are completely alone, the universe itself will teach you everything you need to know. You just have to look and listen.",
        "lesson": "You don't need a formal guru to learn the deepest truths. Watch a tree: it stands firm in storms, gives shade without asking, and sheds its leaves when the season demands. Be like the tree. Watch a river: it flows around obstacles, purifies itself as it moves, and always reaches the ocean eventually. Be like the river. Nature is speaking constantly. Are you listening?",
        "reflect": "Go outside today and find one thing in nature that has something to teach you. A bird, a plant, the wind. Ask it: 'What wisdom do you have for me today?' And listen for the answer — not in words, but in feeling.",
        "quote": "The earth, the wind, the sky, the water, the fire, the moon, the sun, the pigeon, the python, the ocean, the moth, the honeybee, the elephant, the deer, the fish, the prostitute Pingala, the osprey, the child, the maiden, the arrow-maker, the spider, and the wasp — these are my 24 gurus. From each I learned something the scriptures could not teach."
    },
    {
        "name": "The Queen Who Walked Into the Earth",
        "source_text": "Valmiki Ramayana — Uttara Kanda",
        "subtitle": "Sita's final act of strength and grace",
        "query": "Sita Ramayana queen strength painting art",
        "story": "After the war, after the coronation, after years of ruling Ayodhya, Ram heard rumors about Sita. His subjects whispered: 'How could a queen who lived in another man's palace be pure?' Ram, bound by his duty as a king, made a choice that has haunted readers for millennia. He banished Sita to the forest — pregnant, alone, heartbroken. But Sita did not break. She found shelter in Valmiki's ashram and raised her twin sons, Lava and Kusha, with strength and dignity. Years later, Ram asked her to prove her purity one more time. And Sita, who had been tested in fire, who had been banished without complaint, who had raised her children alone — Sita looked at the assembly and said: 'If I have been faithful in thought, word, and deed, let Mother Earth receive me.' The ground opened. A golden throne rose. And Sita was taken into the arms of her mother, the Earth. She did not burn. She did not break. She went home.",
        "insight": "Sita's return to the Earth is one of the most powerful endings in world literature. After everything — the kidnapping, the war, the fire test, the banishment — she does not break down, does not curse, does not beg. She simply makes a statement of her truth and lets the universe respond. And the universe does respond: the Earth itself opens to receive her. Sita is not a victim — she is one of the strongest characters in the Ramayana. Her strength is not in fighting but in enduring with integrity. She proves that grace under pressure is the highest form of power. Her return to the Earth is not an escape — it is a triumphant homecoming.",
        "lesson": "The world may test you. People may doubt you. Life may seem unfair. But your integrity is something no one can take from you. Like Sita, you can face the fire and not be consumed. Like Sita, you can be banished and still thrive. And like Sita, when the time comes, the universe itself will recognize your truth and welcome you home.",
        "reflect": "When has your integrity been tested? Did you stay true to yourself even when it was costly? That moment of staying true was your own Agni Pariksha — and you passed it.",
        "quote": "If I have been faithful in thought, word, and deed — then let Mother Earth receive me. And the Earth opened. Truth, when spoken with complete conviction, moves the very ground beneath your feet."
    },
]

def fetch_json(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "MythologyDigest/1.0 (hermes)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def try_fetch_json(url: str) -> dict | None:
    try:
        return fetch_json(url)
    except Exception:
        return None

def pick_topic(today: dt.date) -> dict:
    return TOPICS[int(today.strftime("%Y%m%d")) % len(TOPICS)]

def _wikipedia_search_term(topic: dict) -> str:
    """Get a specific Wikipedia search term for image lookup."""
    name = topic["name"]
    mapping = {
        "Rantideva's Last Morsel": "Rantideva",
        "Abhimanyu in the Chakravyuha": "Abhimanyu",
        "Savitri and Satyavan": "Savitri_and_Satyavan",
        "The Birth of the Pandavas": "Pandava",
        "The Dog at Heaven's Gate": "Yudhishthira",
        "Karna's Promise to Kunti": "Karna",
        "When Hanuman Found His Lord": "Hanuman",
        "The Bridge That Defied the Ocean": "Ram Setu",
        "The Mountain of Devotion": "Hanuman",
        "The Choice That Defined Dharma": "Vibhishana",
        "The Line Drawn in Love": "Lakshmana",
        "The Promise That Defined a Life": "Bhishma",
        "The Generosity That Knew No Bounds": "Karna",
        "When Help Comes From Where You Least Expect": "Draupadi",
        "The Student Who Taught the Guru": "Ekalavya",
        "The Cosmic Storyteller's Scribe": "Ganesha",
        "The Great Churning": "Samudra Manthan",
        "The Boy Who Would Not Break": "Narasimha",
        "The Poison That Became a Blessing": "Shiva",
        "The Friendship That Changed Everything": "Krishna",
        "The River That Flows From Grace": "Ganga",
        "The Riddle of Life Itself": "Yudhishthira",
        "The Final Gift of Understanding": "Krishna",
        "The Queen Who Walked Into the Earth": "Sita",
    }
    return mapping.get(name, name)


def wiki_image(topic: dict) -> dict:
    """Find an image for the topic — Wikipedia thumbnail first, then Commons."""
    search_term = _wikipedia_search_term(topic)

    # Try Wikipedia page images first
    wp_params = urllib.parse.urlencode({
        "action": "query", "format": "json", "titles": search_term,
        "prop": "pageimages", "pithumbsize": 1000, "pilimit": 1,
    })
    wp_data = try_fetch_json(f"{WIKI_IMAGE}?{wp_params}")
    if wp_data and "query" in wp_data:
        for _, page in wp_data["query"].get("pages", {}).items():
            thumb = page.get("thumbnail", {})
            if thumb.get("source"):
                return {
                    "url": thumb["source"],
                    "title": page.get("title", search_term),
                    "description": f"{search_term} — Wikipedia",
                    "source": "Wikipedia",
                    "source_url": f"https://en.wikipedia.org/wiki/{urllib.parse.quote(search_term.replace(' ', '_'))}"
                }

    # Fallback: Wikimedia Commons with Indian-art-focused queries
    commons_queries = [
        search_term + " painting indian",
        search_term + " mahabharata ramayana art",
        search_term + " mythology painting",
        search_term + " hindu art",
        topic["query"].split()[0] + " indian painting",
    ]
    seen_urls = set()
    for cq in commons_queries:
        search_params = urllib.parse.urlencode({
            "action": "query", "format": "json", "list": "search",
            "srsearch": cq, "srnamespace": "6", "srlimit": 5, "srprop": "title",
        })
        data = try_fetch_json(f"{COMMONS_URL}?{search_params}")
        if not data or "query" not in data:
            continue
        for sr in data["query"].get("search", []):
            title = sr.get("title", "")
            img_params = urllib.parse.urlencode({
                "action": "query", "format": "json", "titles": title,
                "prop": "imageinfo", "iiprop": "url|extmetadata|mime", "iiurlwidth": 1000,
            })
            img_data = try_fetch_json(f"{COMMONS_URL}?{img_params}")
            if not img_data or "query" not in img_data:
                continue
            for _, page in img_data["query"].get("pages", {}).items():
                info = page.get("imageinfo", [])
                if not info or not info[0].get("url"):
                    continue
                url = info[0]["url"]
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                mime = info[0].get("mime", "")
                if mime and not mime.startswith("image/jpeg") and not mime.startswith("image/png"):
                    continue
                desc = info[0].get("extmetadata", {}).get("ImageDescription", {}).get("value", "")[:450]
                return {
                    "url": url,
                    "title": page.get("title", title),
                    "description": re.sub(r"\s+", " ", desc).strip()[:300] if desc else f"Illustration of {search_term}",
                    "source": "Wikimedia Commons",
                    "source_url": url
                }
    return {}

def esc(x): return html.escape(str(x), quote=True)

def shloka_html(topic: dict) -> str:
    """Generate the shloka section if the topic has a shloka."""
    if "shloka_sanskrit" not in topic:
        return ""
    sanskrit = topic["shloka_sanskrit"].replace("\n", "<br>")
    translit = topic.get("shloka_translit", "").replace("\n", "<br>")
    trans = topic.get("shloka_translation", "")
    return f"""
<section class="shloka card">
  <div class="eyebrow">The Verse</div>
  <h2>{esc(topic.get('source_text', 'Sacred Text'))}</h2>
  <div class="sanskrit">{sanskrit}</div>
  <div class="transliteration">{translit}</div>
  <div class="translation">"{esc(trans)}"</div>
</section>"""

def source_links(topic: dict, image: dict) -> str:
    links = list(topic.get("sources", []))
    if image.get("source_url"):
        links.append((image.get("source", "Image Source"), image["source_url"]))
    seen = set()
    return "\n".join(f'<li><a href="{esc(u)}">{esc(l)}</a></li>'
                     for l, u in links if not (u in seen or seen.add(u)))

def build_html(topic: dict, image: dict, today: dt.date) -> str:
    name = topic["name"]
    nums = topic.get("numbers", [])
    hero = image.get("url", "")
    hero_desc = image.get("description", "")
    hero_title = image.get("title", name)

    fact_cards = "\n".join(
        f'<div class="stat"><span>{esc(k)}</span><strong>{esc(v)}</strong></div>'
        for k, v in nums
    )

    h = int(hashlib.sha256(name.encode()).hexdigest()[:2], 16) % 360
    h2 = (h + 30) % 360
    today_label = today.strftime("%A, %B %-d, %Y")
    if os.name == "nt":
        today_label = today.strftime("%A, %B %#d, %Y")

    story = topic.get("story", "")
    insight = topic.get("insight", "")
    lesson = topic.get("lesson", "")
    reflect = topic.get("reflect", "")
    quote = topic.get("quote", "")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mythology Field Note — {esc(name)}</title>
<style>
:root {{ --h: {h}; --h2: {h2}; --ink: #1a1423; --muted: #6b5c6b; --line: #e8d5c4; --accent: hsl(var(--h), 70%, 40%); --accent2: hsl(var(--h2), 65%, 45%); --gold: hsl(42, 85%, 50%); }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: 'Georgia', 'Noto Serif', 'Times New Roman', serif; color: var(--ink); background: radial-gradient(circle at 10% 10%, hsl(var(--h), 70%, 92%), transparent 40rem), radial-gradient(circle at 90% 90%, hsl(var(--h2), 60%, 90%), transparent 40rem), linear-gradient(180deg, #fef8f0, #f5efe6); }}
.wrap {{ max-width: 1100px; margin: 0 auto; padding: 40px 22px 60px; }}
.mast {{ display: flex; gap: 20px; align-items: flex-start; margin-bottom: 28px; }}
.badge {{ flex-shrink: 0; width: 64px; height: 64px; border-radius: 50%; display: grid; place-items: center; color: #fff; font-size: 32px; background: linear-gradient(135deg, var(--accent), var(--gold)); box-shadow: 0 4px 20px rgba(0,0,0,0.15); }}
.kicker {{ color: var(--accent); font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; font-size: 12px; margin-bottom: 4px; }}
h1 {{ font-size: clamp(36px, 7vw, 72px); line-height: 0.95; margin: 4px 0 8px; letter-spacing: -0.03em; color: var(--ink); }}
.subtitle {{ font-size: clamp(18px, 2.5vw, 30px); color: #4a3f4a; margin: 0; max-width: 850px; font-style: italic; }}
.source-tag {{ display: inline-block; margin-top: 6px; padding: 4px 14px; background: var(--accent); color: #fff; border-radius: 999px; font-size: 12px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }}
.hero {{ margin-top: 24px; display: grid; grid-template-columns: 1.3fr 0.7fr; gap: 22px; align-items: stretch; }}
.image-card, .card {{ border: 1px solid rgba(26, 20, 35, 0.10); background: rgba(255, 255, 255, 0.80); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); border-radius: 28px; overflow: hidden; box-shadow: 0 8px 40px rgba(26, 20, 35, 0.08); }}
.image-card img {{ display: block; width: 100%; height: 480px; object-fit: cover; background: #1a1423; }}
.caption {{ padding: 16px 20px; color: var(--muted); font-size: 14px; line-height: 1.4; }}
.card {{ padding: 28px; }}
.eyebrow {{ color: var(--accent); font-weight: 800; letter-spacing: 0.1em; text-transform: uppercase; font-size: 11px; }}
h2 {{ font-size: 28px; letter-spacing: -0.02em; margin: 6px 0 14px; color: var(--ink); }}
p, .story-text {{ font-size: 17px; line-height: 1.7; color: #2a2030; }}
.stats {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-top: 16px; }}
.stat {{ padding: 12px 14px; background: #fff; border: 1px solid var(--line); border-radius: 16px; }}
.stat span {{ display: block; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.07em; font-weight: 700; }}
.stat strong {{ display: block; margin-top: 3px; font-size: 16px; color: var(--ink); }}
.grid {{ display: grid; grid-template-columns: 1fr; gap: 22px; margin-top: 22px; }}
.section-card {{ border-left: 5px solid var(--accent); }}
.section-insight {{ border-left: 5px solid var(--gold); }}
.section-lesson {{ border-left: 5px solid #2e7d32; }}
.section-reflect {{ background: linear-gradient(135deg, hsl(var(--h), 70%, 95%), #fff); border: 1px solid var(--line); }}
.section-quote {{ text-align: center; font-size: 22px; font-style: italic; color: var(--accent); padding: 32px; border: none; background: linear-gradient(135deg, hsl(var(--h), 70%, 92%), hsl(var(--h2), 60%, 90%)); }}
.section-quote blockquote {{ margin: 0; line-height: 1.5; }}
.shloka {{ margin-top: 22px; text-align: center; }}
.sanskrit {{ font-size: 22px; line-height: 1.8; color: #1a1423; margin: 16px 0 12px; padding: 20px; background: rgba(255,255,255,0.6); border-radius: 16px; border: 1px solid var(--line); font-family: 'Noto Sans Devanagari', 'Sanskrit Text', 'Nirmala UI', serif; }}
.transliteration {{ font-size: 16px; color: #4a3f4a; font-style: italic; margin: 8px 0; letter-spacing: 0.02em; }}
.translation {{ font-size: 18px; color: var(--accent); font-weight: 600; margin: 12px 0 4px; line-height: 1.5; max-width: 700px; margin-left: auto; margin-right: auto; }}
.sources {{ margin-top: 22px; }}
.sources ul {{ margin: 12px 0 0; padding-left: 20px; }}
.sources li {{ margin-bottom: 6px; }}
a {{ color: var(--accent); font-weight: 700; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.footer {{ margin-top: 32px; padding-top: 20px; border-top: 1px solid var(--line); color: var(--muted); font-size: 13px; text-align: center; }}
@media (max-width: 820px) {{ .hero{{grid-template-columns:1fr}}.image-card img{{height:320px}}.stats{{grid-template-columns:1fr}}.mast{{flex-direction:column;align-items:flex-start}} }}
</style>
</head>
<body>
<main class="wrap">

<header class="mast">
  <div class="badge">🪷</div>
  <div>
    <div class="kicker">Mythology Field Note · {esc(today_label)}</div>
    <h1>{esc(name)}</h1>
    <p class="subtitle">{esc(topic.get('subtitle', ''))}</p>
    <span class="source-tag">{esc(topic.get('source_text', 'Indian Mythology'))}</span>
  </div>
</header>

<section class="hero">
  <div class="image-card">
    {f'<img src="{esc(hero)}" alt="{esc(name)}" loading="lazy">' if hero else ''}
    <div class="caption"><strong>{esc(hero_title)}</strong><br>{esc(hero_desc[:300]) if hero_desc else "Wikimedia Commons illustration"}</div>
  </div>
  <aside class="card">
    <div class="eyebrow">At a Glance</div>
    <h2>Key Details</h2>
    <div class="stats">{fact_cards}</div>
  </aside>
</section>

{shloka_html(topic)}

<section class="grid">
  <article class="card section-card">
    <div class="eyebrow">The Story</div>
    <h2>What Happened</h2>
    <div class="story-text">{esc(story)}</div>
  </article>
  <article class="card section-insight">
    <div class="eyebrow">Why It Matters</div>
    <h2>The Insight</h2>
    <div class="story-text">{esc(insight)}</div>
  </article>
  <article class="card section-lesson">
    <div class="eyebrow">Today's Lesson</div>
    <h2>How to Apply This</h2>
    <div class="story-text">{esc(lesson)}</div>
  </article>
  <article class="card section-reflect">
    <div class="eyebrow">Reflect On This</div>
    <h2>A Question for You</h2>
    <div class="story-text">{esc(reflect)}</div>
  </article>
  <article class="card section-quote">
    <blockquote>{esc(quote)}</blockquote>
  </article>
</section>

<section class="sources card">
  <div class="eyebrow">Further Reading</div>
  <h2>Source Trail</h2>
  <p>References from Valmiki Ramayana, Mahabharata, Bhagavata Purana, and academic sources.</p>
  <ul>{source_links(topic, image)}</ul>
</section>

<div class="footer">
  <p>🪷 Generated by Indian Mythology Daily Digest — a new story every day</p>
  <p>📖 Read the originals at <a href="https://vedabase.io">Vedabase.io</a> · <a href="https://www.valmikiramayan.net/">Valmiki Ramayana</a> · <a href="https://www.gitapress.org/">Gita Press</a></p>
</div>

</main>
</body>
</html>"""


GIT_REMOTE = os.environ.get("MYTHOLOGY_GIT_REMOTE",
    "https://github.com/shenoyabhijith/indian-mythology-digest.git")
GIT_BRANCH = "main"


def push_to_github(out_dir: Path, html_path: Path) -> bool:
    """Commit today's article and push to GitHub."""
    try:
        git_dir = out_dir / ".git"
        if not git_dir.exists():
            # Init repo if not already one
            _run_cmd(["git", "init"], cwd=out_dir)
            _run_cmd(["git", "branch", "-m", GIT_BRANCH], cwd=out_dir)
            _run_cmd(["git", "remote", "add", "origin", GIT_REMOTE], cwd=out_dir)
        # Configure committer
        _run_cmd(["git", "config", "user.email", "shenoyabhijith@users.noreply.github.com"], cwd=out_dir)
        _run_cmd(["git", "config", "user.name", "shenoyabhijith"], cwd=out_dir)
        # Add files (relative paths within repo)
        archive_rel = f"archive/{html_path.name}"
        _run_cmd(["git", "add", "latest.html", archive_rel, "README.md", "index.html"], cwd=out_dir)
        # Commit (no-op if nothing changed)
        today = dt.datetime.now(dt.UTC).strftime("%B %d, %Y")
        _run_cmd(["git", "commit", "-m", f"📖 Mythology digest — {today}"], cwd=out_dir,
                 check=False)
        # Push: get token from gh CLI at runtime (safer than stored in git config)
        try:
            import subprocess
            token = subprocess.run(
                ["/opt/data/bin/gh", "auth", "token"],
                capture_output=True, text=True, timeout=10, env={**os.environ}
            ).stdout.strip()
        except Exception:
            token = ""
        if token:
            remote_url = GIT_REMOTE.replace("https://", f"https://x-access-token:{token}@")
            _run_cmd(["git", "remote", "set-url", "origin", remote_url], cwd=out_dir)
        _run_cmd(["git", "push", "origin", GIT_BRANCH], cwd=out_dir, timeout=30)
        return True
    except Exception as exc:
        print(f"[mythology-digest] GitHub push failed: {exc}", file=__import__("sys").stderr)
        return False


def _run_cmd(args: list[str], cwd: Path, timeout: int = 15, check: bool = True) -> None:
    import subprocess
    result = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    if check and result.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}")


def main() -> int:
    today = dt.datetime.now(dt.UTC).date()
    topic = pick_topic(today)
    image = wiki_image(topic)

    html_text = build_html(topic, image, today)

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r"[^a-z0-9]+", "-", topic["name"].lower()).strip("-")
    html_path = ARCHIVE_DIR / f"mythology-field-note-{today.isoformat()}-{slug}.html"
    (OUT_DIR / "latest.html").write_text(html_text, encoding="utf-8")
    html_path.write_text(html_text, encoding="utf-8")

    # Rebuild archive index
    _build_archive_index(OUT_DIR, ARCHIVE_DIR)

    # Push to GitHub
    push_to_github(OUT_DIR, html_path)

    # Print website link instead of MEDIA: path
    site_url = "https://shenoyabhijith.github.io/indian-mythology-digest/"
    print(f"🌐 {site_url}")
    return 0


def _build_archive_index(out_dir: Path, archive_dir: Path) -> None:
    """Generate archive index.html listing all articles."""
    import re as _re
    articles = []
    for f in sorted(archive_dir.glob("*.html"), reverse=True):
        html = f.read_text(encoding="utf-8")
        title = ""
        m = _re.search(r'<h1>([^<]+)</h1>', html)
        if m: title = m.group(1)
        date_str = ""
        m = _re.search(r'Mythology Field Note · ([^<]+)', html)
        if m: date_str = m.group(1).strip()
        source = ""
        m = _re.search(r'<span class="source-tag">([^<]+)</span>', html)
        if m: source = m.group(1).strip()
        subtitle = ""
        m = _re.search(r'<p class="subtitle">([^<]+)</p>', html)
        if m: subtitle = m.group(1).strip()
        excerpt = ""
        m = _re.search(r'<div class="story-text">([^<]+)', html)
        if m: excerpt = m.group(1).strip()[:200] + "..."
        articles.append({
            "title": title or f.name, "date": date_str or f.name[:10],
            "source": source, "subtitle": subtitle, "excerpt": excerpt,
            "file": f.name
        })

    cards = "\n".join(
        f'<a href="archive/{a["file"]}" class="card">'
        f'<span class="date">{a["date"]}</span>{" · " + a["source"] if a["source"] else ""}'
        f'<h3>{a["title"]}</h3>'
        f'{"<br><em>" + a["subtitle"] + "</em>" if a["subtitle"] else ""}'
        f'<p>{a["excerpt"]}</p></a>'
        for a in articles
    )

    index = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>🪷 Indian Mythology Daily Digest</title>
<style>:root{{--ink:#1a1423;--muted:#6b5c6b;--accent:#b84d3c;}}
*{{box-sizing:border-box}}body{{margin:0;font-family:Georgia,'Noto Serif',serif;color:var(--ink);background:linear-gradient(180deg,#fef8f0,#f5efe6)}}
.wrap{{max-width:700px;margin:0 auto;padding:60px 22px;text-align:center}}
h1{{font-size:clamp(36px,7vw,64px);margin:12px 0 4px;letter-spacing:-.02em}}
.sub{{font-size:20px;color:#4a3f4a;font-style:italic;margin:0 0 20px}}
.cta a{{display:inline-block;padding:12px 32px;background:var(--accent);color:#fff;border-radius:999px;font-size:17px;font-weight:700;text-decoration:none;box-shadow:0 4px 16px rgba(184,77,60,.3)}}
.cta a:hover{{transform:translateY(-2px)}}
.sister{{margin-top:40px}}
.sister a{{color:var(--accent);font-size:15px;text-decoration:none;border-bottom:1px dashed var(--accent)}}
.footer{{margin-top:60px;color:var(--muted);font-size:13px}}
.footer a{{color:var(--accent)}}
</style></head><body><div class="wrap">
<h1>🪷 Indian Mythology Daily Digest</h1>
<p class="sub">Stories &amp; Insights from India's Great Epics</p>
<div class="cta"><a href="latest.html">📖 Read Today's Article</a></div>
<div class="sister"><a href="https://shenoyabhijith.github.io/daily-space-digest/">☄️ Also visit: Daily Space Field Notes</a></div>
<div class="footer"><p>🪷 A new story every evening · <a href="https://github.com/shenoyabhijith/indian-mythology-digest">GitHub</a></p></div>
</div></body></html>"""
    (out_dir / "index.html").write_text(index, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
