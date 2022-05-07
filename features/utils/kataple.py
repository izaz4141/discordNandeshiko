from discord import Embed, User, Message

import datetime
import random

popular_words = open("./data/kamus/kata_4.txt").read().splitlines()
all_words = set(word.strip() for word in open("./data/kamus/kata_4.txt"))

EMOJI_CODES = {
    "green": {
        "a": "<:ag:961281977074475138>",
        "b": "<:bg:961281977275809814>",
        "c": "<:cg:961281977103835227> ",
        "d": "<:dg:961281977569378314>",
        "e": "<:eg:961281977615515648>",
        "f": "<:fg:961281977615527956>",
        "g": "<:gg:961281977158352937>",
        "h": "<:hg:961281977196113953>",
        "i": "<:ig:961281977615523921>",
        "j": "<:jg:961281977829441546>",
        "k": "<:kg:961281977862991942>",
        "l": "<:lg:961281977779122206>",
        "m": "<:mg:961281978018185286>",
        "n": "<:ng:961281977896546304>",
        "o": "<:og:961281977732980847>",
        "p": "<:pg:961281977883975700>",
        "q": "<:qg:961281977821044817>",
        "r": "<:rg:961281977976233984>",
        "s": "<:sg:961281978026565712>",
        "t": "<:tg:961281978047528960>",
        "u": "<:ug:961281978009800704>",
        "v": "<:vg:961282673047916655>",
        "w": "<:wg:961281978005602354>",
        "x": "<:xg:961281978018181200>",
        "y": "<:yg:961282673521868872>",
        "z": "<:zg:961282673404420136>",
    },
    "yellow": {
        "a": "<:1f1e6:961282556127502347>",
        "b": "<:1f1e7:961282556140072980>",
        "c": "<:1f1e8:961282556387532851>",
        "d": "<:1f1e9:961282556467232818>",
        "e": "<:1f1ea:961282556454645771>",
        "f": "<:1f1eb:961282556676956210>",
        "g": "<:1f1ec:961282556509167617>",
        "h": "<:1f1ed:961282556777607188>",
        "i": "<:1f1ee:961282556819566613>",
        "j": "<:1f1ef:961282556660174890>",
        "k": "<:1f1f0:961282557012484167>",
        "l": "<:1f1f1:961282557138337842>",
        "m": "<:1f1f2:961282557146705930>",
        "n": "<:1f1f3:961282557218005052>",
        "o": "<:1f1f4:961282557209616504>",
        "p": "<:1f1f5:961282557280923748>",
        "q": "<:1f1f6:961282557297709056>",
        "r": "<:1f1f7:961282557377388584>",
        "s": "<:1f1f8:961282557381578832>",
        "t": "<:1f1f9:961282557419331654>",
        "u": "<:1f1fa:961282557423550465>",
        "v": "<:1f1fb:961282557448704070>",
        "w": "<:1f1fc:961282557171879968>",
        "x": "<:1f1fd:961282557394182184>",
        "y": "<:1f1fe:961282557406748692>",
        "z": "<:1f1ff:961282557377392701>",
    },
    "gray": {
        "a": "<:1f1e6:961280460363816970>",
        "b": "<:1f1e7:961280460443516988>",
        "c": "<:1f1e8:961280460913266738>",
        "d": "<:1f1e9:961280460791611452>",
        "e": "<:1f1ea:961280460749676604>",
        "f": "<:1f1eb:961280460737106010>",
        "g": "<:1f1ec:961280460850335895>",
        "h": "<:1f1ed:961280460875513907>",
        "i": "<:1f1ee:961280460816785509>",
        "j": "<:1f1ef:961280460707733596>",
        "k": "<:1f1f0:961280461424967750>",
        "l": "<:1f1f1:961281867854786562>",
        "m": "<:1f1f2:961280461345288283>",
        "n": "<:1f1f3:961280461370458112>",
        "o": "<:1f1f4:961280461437546496>",
        "p": "<:1f1f5:961280461433372682>",
        "q": "<:1f1f6:961280461030703185>",
        "r": "<:1f1f7:961280461445935205>",
        "s": "<:1f1f8:961280461659840512>",
        "t": "<:1f1f9:961280461487882250>",
        "u": "<:1f1fa:961280461685006436>",
        "v": "<:1f1fb:961280461592727662>",
        "w": "<:1f1fc:961280461764714526>",
        "x": "<:1f1fd:961280461664043058>",
        "y": "<:1f1fe:961280461273964585>",
        "z": "<:1f1ff:961280461676609626>",
    },
}


def generate_colored_word(guess: str, answer: str) -> str:
    """
    Builds a string of emoji codes where each letter is
    colored based on the key:
    - Same letter, same place: Green
    - Same letter, different place: Yellow
    - Different letter: Gray
    Args:
        word (str): The word to be colored
        answer (str): The answer to the word
    Returns:
        str: A string of emoji codes
    """
    colored_word = [EMOJI_CODES["gray"][letter] for letter in guess]
    guess_letters = list(guess)
    answer_letters = list(answer)
    # change colors to green if same letter and same place
    for i in range(len(guess_letters)):
        if guess_letters[i] == answer_letters[i]:
            colored_word[i] = EMOJI_CODES["green"][guess_letters[i]]
            answer_letters[i] = None
            guess_letters[i] = None
    # change colors to yellow if same letter and not the same place
    for i in range(len(guess_letters)):
        if guess_letters[i] is not None and guess_letters[i] in answer_letters:
            colored_word[i] = EMOJI_CODES["yellow"][guess_letters[i]]
            answer_letters[answer_letters.index(guess_letters[i])] = None
    return "".join(colored_word)


def generate_blanks(n: int) -> str:
    """
    Generate a string of n blank white square emoji characters
    Returns:
        str: A string of white square emojis
    """
    return "\N{WHITE MEDIUM SQUARE}" * n


def generate_puzzle_embed(user: User, puzzle_id: int) -> Embed:
    """
    Generate an embed for a new puzzle given the puzzle id and user
    Args:
        user (nextcord.User): The user who submitted the puzzle
        puzzle_id (int): The puzzle ID
    Returns:
        nextcord.Embed: The embed to be sent
    """
    n = len(popular_words[puzzle_id])
    embed = Embed(title="Wordle Clone")
    embed.description = "\n".join([generate_blanks(n)] * 6)
    embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    embed.set_footer(
        text=f"ID: {puzzle_id}\n"
        "Untuk menebak, balas pesan ini!"
    )
    return embed


def update_embed(embed: Embed, guess: str) -> Embed:
    """
    Updates the embed with the new guesses
    Args:
        embed (nextcord.Embed): The embed to be updated
        puzzle_id (int): The puzzle ID
        guess (str): The guess made by the user
    Returns:
        nextcord.Embed: The updated embed
    """
    puzzle_id = int(embed.footer.text.split()[1])
    answer = popular_words[puzzle_id]
    if len(guess) != len(answer):
        return
    colored_word = generate_colored_word(guess, answer)
    n = len(answer)
    empty_slot = generate_blanks(n)
    # replace the first blank with the colored word
    embed.description = embed.description.replace(empty_slot, colored_word, 1)
    # check for game over
    num_empty_slots = embed.description.count(empty_slot)
    if guess == answer:
        if num_empty_slots == 0:
            embed.description += "\n\nPhew!"
        if num_empty_slots == 1:
            embed.description += "\n\nGreat!"
        if num_empty_slots == 2:
            embed.description += "\n\nSplendid!"
        if num_empty_slots == 3:
            embed.description += "\n\nImpressive!"
        if num_empty_slots == 4:
            embed.description += "\n\nMagnificent!"
        if num_empty_slots == 5:
            embed.description += "\n\nGenius!"
    elif num_empty_slots == 0:
        embed.description += f"\n\nThe answer was {answer}!"
    return embed


def is_valid_word(word: str) -> bool:
    """
    Validates a word
    Args:
        word (str): The word to validate
    Returns:
        bool: Whether the word is valid
    """
    return word in all_words


def random_puzzle_id() -> int:
    """
    Generates a random puzzle ID
    Returns:
        int: A random puzzle ID
    """
    return random.randint(0, len(popular_words) - 1)


def daily_puzzle_id() -> int:
    """
    Calculates the puzzle ID for the daily puzzle
    Returns:
        int: The puzzle ID for the daily puzzle
    """
    # calculate days since 1/1/2022 and mod by the number of puzzles
    num_words = len(popular_words)
    time_diff = datetime.datetime.now().date() - datetime.date(2022, 1, 1)
    return time_diff.days % num_words


def is_game_over(embed: Embed) -> bool:
    """
    Checks if the game is over in the embed
    Args:
        embed (nextcord.Embed): The embed to check
    Returns:
        bool: Whether the game is over
    """
    return "\n\n" in embed.description



async def process_message_as_guess(
    bot, message: Message
) -> bool:
    """
    Check if a new message is a reply to a Wordle game.
    If so, validate the guess and update the bot's message.
    Args:
        bot (nextcord.Client): The bot
        message (nextcord.Message): The new message to process
    Returns:
        bool: True if the message was processed as a guess, False otherwise
    """
    # get the message replied to
    ref = message.reference
    if not ref or not isinstance(ref.resolved, Message):
        return False
    parent = ref.resolved
    
    # if the parent message is not the bot's message, ignore it
    if parent.author.id != bot.user.id:
        return False

    # check that the message has embeds
    if not parent.embeds:
        return False

    embed = parent.embeds[0]

    guess = message.content.lower()

    # check that the user is the one playing
    if (
        embed.author.name != message.author.name
        or embed.author.icon_url != message.author.display_avatar.url
    ):
        reply = "Hanya orang yang memulai game yang dapat menebak."
        if embed.author:
            reply = f"Game ini dimulai oleh {embed.author.name}. " + reply
        await message.reply(reply, delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    # check that the game is not over
    if is_game_over(embed):
        await message.reply(
            "Wordle telah berakhir, coba mulai ulang game", delete_after=5
        )
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    # check that a single word is in the message
    if len(message.content.split()) > 1:
        await message.reply(
            "Tolong tebak dengan satu kata saja", delete_after=5
        )
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    # check that the word is valid
    if not is_valid_word(guess):
        await message.reply("That is not a valid word", delete_after=5)
        try:
            await message.delete(delay=5)
        except Exception:
            pass
        return True

    # update the embed
    embed = update_embed(embed, guess)
    await parent.edit(embed=embed)

    # attempt to delete the message
    try:
        await message.delete()
    except Exception:
        pass

    return True