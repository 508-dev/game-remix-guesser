from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.sql.expression import func
import random

from . import models, schemas, internal

# REMIX
def get_remix(db: Session, remix_id: int):
    return db.query(models.Remix).filter(models.Remix.id == remix_id).first()

def get_remix_by_ocremix_id(db: Session, ocremix_id: str):
    return db.query(models.Remix).filter(models.Remix.ocremix_remix_id == ocremix_id).first()

def get_remixes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Remix).offset(skip).limit(limit).all()

def get_remix_by_title(db: Session, remix_title: str):
    return db.query(models.Remix).filter_by(remix_title=remix_title)

def create_remix(db: Session, remix: schemas.RemixCreate, remix_artist_id: int, remix_original_song_id: int):
    db_remix = models.Remix(
        **remix,
        remix_artist_id=remix_artist_id,
        remix_original_song_id=remix_original_song_id
    )
    db.add(db_remix)
    db.commit()
    db.refresh(db_remix)
    return db_remix

def deep_create_remix(
        db: Session,
        remix: schemas.RemixCreate,
        remix_artist: schemas.RemixArtistCreate,
        remix_original_song: schemas.OriginalSongCreate,
        original_artist: schemas.OriginalArtistCreate,
        videogame: schemas.VideogameCreate):

    remix_artist_db = get_remix_artist_by_name(db, remix_artist['remix_artist_name'])

    if remix_artist_db is None:
        remix_artist_db = create_remix_artist(db, remix_artist)

    remix_original_song_db = get_original_song_by_title(db, original_song_title=remix_original_song['original_song_title'][0])

    if remix_original_song_db is None:
        remix_original_song_db = deep_create_original_song(db, remix_original_song, original_artist, videogame)

    return create_remix(db, remix, remix_artist_db.id, remix_original_song_db.id)


# REMIX ARTIST

def get_remix_artist(db: Session, remix_artist_id: int):
    return db.query(models.RemixArtist).filter(models.RemixArtist.id == remix_artist_id).first()

def get_remix_artist_by_name(db: Session, remix_artist_name: str):
    query = db.query(models.RemixArtist).filter_by(remix_artist_name=remix_artist_name).first()
    return query

def create_remix_artist(db: Session, remix_artist: schemas.RemixArtistCreate):
    db_remix_artist = models.RemixArtist(**remix_artist)
    db.add(db_remix_artist)
    db.commit()
    db.refresh(db_remix_artist)
    return db_remix_artist

# ORIGINAL SONG

def get_original_song(db: Session, original_song_id: int):
    return db.query(models.OriginalSong).filter(models.OriginalSong.id == original_song_id).first()

def get_original_song_by_title(db: Session, original_song_title: str):
    return db.query(models.OriginalSong).filter_by(original_song_title=original_song_title).first()

def create_original_song(db: Session, original_song: schemas.OriginalSongCreate, original_song_artist_id, original_song_videogame_id):
    db_original_song = models.OriginalSong(
        **original_song,
        original_song_artist_id=original_song_artist_id,
        original_song_videogame_id=original_song_videogame_id
        )
    db.add(db_original_song)
    db.commit()
    db.refresh(db_original_song)
    return db_original_song

def deep_create_original_song(db: Session, original_song: schemas.OriginalSongCreate, original_artist_create: schemas.OriginalArtistCreate, videogame_create: schemas.VideogameCreate):

    original_artist_db = get_original_artist_by_name(db, original_artist_create['original_artist_name'])

    if (original_artist_db is None):
        # Make song
        original_artist_db = create_original_artist(db, original_artist_create)

    videogame_db = get_videogame_by_title(db, videogame_create['videogame_title'])

    if (videogame_db is None):
        videogame_db = create_videogame(db, videogame_create)

    return create_original_song(db, original_song, original_artist_db.id, videogame_db.id)

def get_original_artist(db: Session, original_artist_id: int):
    return db.query(models.OriginalArtist).filter(models.OriginalArtist.id == original_artist_id).first()

def create_original_artist(db: Session, original_artist: schemas.OriginalArtistCreate):
    db_original_artist = models.OriginalArtist(**original_artist)
    db.add(db_original_artist)
    db.commit()
    db.refresh(db_original_artist)
    return db_original_artist

def get_original_artist_by_name(db: Session, original_artist_name: str):
    return db.query(models.OriginalArtist).filter_by(original_artist_name=original_artist_name).first()

# VIDEOGAME

def get_videogame(db: Session, videogame_id: int):
    return db.query(models.Videogame).filter(models.Videogame.id == videogame_id).first()

def get_videogame_by_title(db: Session, videogame_title):
    return db.query(models.Videogame).filter_by(videogame_title=videogame_title).first()

def create_videogame(db: Session, videogame: schemas.VideogameCreate):
    db_videogame = models.Videogame(**videogame)
    db.add(db_videogame)
    db.commit()
    db.refresh(db_videogame)
    return db_videogame

# GAME

 # def create_game(db: Session):
#     game = models.Game({ 'score': 0})
#     db.add(game)
#     db.commit()
#     db.refresh(game)
#     return game

# def get_game_by_id(db: Session, game_id: int):
#     game = db.query(models.Game).filter(models.Game.id == game_id).first()

# QUESTION

def create_question(db: Session,
                    correct_remix: schemas.Remix,
                    choice_1_remix: schemas.Remix,
                    choice_2_remix: schemas.Remix,
                    choice_3_remix: schemas.Remix,
                    ):
    question = models.Question(
        correct_remix_id= correct_remix.id,
        choice_1_remix_id= choice_1_remix.id,
        choice_2_remix_id= choice_2_remix.id,
        choice_3_remix_id= choice_3_remix.id
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

def generate_question(db: Session):
    games = db.query(models.Videogame).order_by(func.random()).limit(4)
    questions = (db.query(models.Remix)
                 .join(models.OriginalSong)
                 .join(games)
                 .distinct(models.OriginalSong.original_song_videogame_id)
                 .order_by(models.OriginalSong.original_song_videogame_id, func.random()))
    internal.log_error(questions)
    response = construct_frontend_question(questions)
    return response

def construct_frontend_question(questions):
    # Apparently, it's 1-indexed?
    # limit(4) takes items [1, 2, 3, 4] not [0, 1, 2, 3]
    # Am I crazy? Why is that??
    choices = []
    # Ok, not only that, apparently indexing is indeterminate?
    # I get different results if I index at different times
    # Run through list twice for now, it's only 4 items
    for question in questions:
        choices.append(question)

    response = models.QuestionPackage(
        choices=[],
        question=models.Question(
            remix_youtube_url=choices[0].remix_youtube_url,
            secret_id=choices[0].secret_id,
        )
    )

    for question in choices:
        response.choices.append(models.Choice(
            origin_game= question.remix_original_song.original_song_videogame.videogame_title,
            public_id= question.public_id
        ))
    random.shuffle(response.choices)
    return response

def match_public_id_to_secret_id(db: Session, public_id: int, secret_id: int):
    return db.query(models.Remix).filter(and_(models.Remix.secret_id == secret_id, models.Remix.public_id == public_id)).first()


# Oops, found a better way with public/secret key pairs
# Oh well
def generate_question_deprecated(db: Session):
    remix_without_question = find_remix_without_question(db)
    if remix_without_question is None:
        internal.log_error("no more remixes without questions maybe?")
        return None
    choice_1 = db.query(models.Remix).filter(models.Remix.id != remix_without_question.id).order_by(func.random()).first()
    choice_2 = db.query(models.Remix).filter(models.Remix.id != remix_without_question.id).order_by(func.random()).first()
    choice_3 = db.query(models.Remix).filter(models.Remix.id != remix_without_question.id).order_by(func.random()).first()
    question = create_question(db, correct_remix=remix_without_question, choice_1_remix=choice_1, choice_2_remix=choice_2, choice_3_remix=choice_3)
    return question

# Also deprecated for now
def find_remix_without_question(db: Session):
    # Compare Question table against Remix
    # Find Remixes without Questions
    # I bet there's a super smarty pants way to do this
    # oh well, this works
    subquery = db.query(models.Question.correct_remix_id)
    result = db.query(models.Remix).filter(models.Remix.id.not_in(subquery))
    return result.first()

# TODO
# For now I don't really know how to prevent the same question being sent twice
# Sessions?
def return_random_question(db: Session):
    return db.query(models.Question).order_by(func.random()).first()
