from django.test import Client, TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from .ai_assistant import DeepSeekAssistant
from .models import Genre, Movie, Movie_hot, Movie_rating, Movie_similarity, User


TEST_DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}


@override_settings(DATABASES=TEST_DATABASES)
class MovieFeatureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.genre_action = Genre.objects.create(name="Action")
        cls.genre_drama = Genre.objects.create(name="Drama")
        cls.genre_scifi = Genre.objects.create(name="Sci-Fi")

        cls.movie_a = Movie.objects.create(
            name="Action Hero",
            imdb_id=101,
            time="120min",
            release_time="2024-01-01",
            intro="Action movie",
            director="Dir A",
            writers="Writer A",
            actors="Actor A",
        )
        cls.movie_a.genre.add(cls.genre_action)

        cls.movie_b = Movie.objects.create(
            name="Drama Life",
            imdb_id=102,
            time="115min",
            release_time="2024-02-01",
            intro="Drama movie",
            director="Dir B",
            writers="Writer B",
            actors="Actor B",
        )
        cls.movie_b.genre.add(cls.genre_drama)

        cls.movie_c = Movie.objects.create(
            name="Interstellar",
            imdb_id=103,
            time="130min",
            release_time="2024-03-01",
            intro="Sci-Fi movie",
            director="Dir C",
            writers="Writer C",
            actors="Actor C",
        )
        cls.movie_c.genre.add(cls.genre_scifi)

        cls.movie_d = Movie.objects.create(
            name="Mixed Epic",
            imdb_id=104,
            time="140min",
            release_time="2024-04-01",
            intro="Hybrid movie",
            director="Dir D",
            writers="Writer D",
            actors="Actor D",
        )
        cls.movie_d.genre.add(cls.genre_action, cls.genre_scifi)

        Movie_similarity.objects.create(
            movie_source=cls.movie_a,
            movie_target=cls.movie_b,
            similarity=0.92,
        )

        cls.user_alice = User.objects.create(
            name="alice",
            password="123456",
            email="alice@example.com",
        )
        cls.user_bob = User.objects.create(
            name="bob",
            password="123456",
            email="bob@example.com",
        )
        cls.user_cindy = User.objects.create(
            name="cindy",
            password="123456",
            email="cindy@example.com",
        )

        Movie_rating.objects.create(user=cls.user_alice, movie=cls.movie_a, score=4.5, comment="great")
        Movie_rating.objects.create(user=cls.user_alice, movie=cls.movie_b, score=3.0, comment="good")
        Movie_rating.objects.create(user=cls.user_bob, movie=cls.movie_a, score=5.0, comment="must watch")
        Movie_rating.objects.create(user=cls.user_bob, movie=cls.movie_c, score=4.5, comment="nice")
        Movie_rating.objects.create(user=cls.user_cindy, movie=cls.movie_b, score=4.0, comment="solid")
        Movie_rating.objects.create(user=cls.user_cindy, movie=cls.movie_d, score=5.0, comment="best")

        Movie_hot.objects.create(movie=cls.movie_c, rating_number=90)
        Movie_hot.objects.create(movie=cls.movie_a, rating_number=120)

    def setUp(self):
        self.client = Client()

    def login_as_alice(self):
        session = self.client.session
        session["user_id"] = self.user_alice.id
        session.save()

    def test_register_success_creates_user_and_redirects(self):
        response = self.client.post(
            reverse("movie:register"),
            {
                "name": "david",
                "password": "abc123",
                "password_repeat": "abc123",
                "email": "david@example.com",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("movie:index"))
        self.assertTrue(User.objects.filter(name="david", email="david@example.com").exists())

    def test_login_success_stores_session(self):
        response = self.client.post(
            reverse("movie:login"),
            {"name": "alice", "password": "123456", "remember": 1},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("movie:index"))
        self.assertEqual(self.client.session["user_id"], self.user_alice.id)

    def test_search_returns_matching_movies(self):
        response = self.client.get(reverse("movie:search"), {"keyword": "Action"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Action Hero")
        self.assertNotContains(response, "Drama Life")
        self.assertEqual(response.context["keyword"], "Action")

    def test_movie_detail_post_updates_existing_rating(self):
        self.login_as_alice()

        response = self.client.post(
            reverse("movie:detail", args=[self.movie_a.id]),
            {"score": 5, "comment": "updated"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("movie:detail", args=[self.movie_a.id]))
        rating = Movie_rating.objects.get(user=self.user_alice, movie=self.movie_a)
        self.assertEqual(rating.score, 5)
        self.assertEqual(rating.comment, "updated")

    def test_history_view_builds_radar_data_for_logged_in_user(self):
        self.login_as_alice()

        response = self.client.get(reverse("movie:history", args=[self.user_alice.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Action Hero")
        self.assertContains(response, "Drama Life")
        self.assertIn("Action", response.context["radar_indicator"])
        self.assertIn("Drama", response.context["radar_indicator"])
        self.assertIn("4.5", response.context["radar_value"])
        self.assertIn("3.0", response.context["radar_value"])

    def test_delete_record_removes_rating(self):
        self.login_as_alice()

        response = self.client.get(reverse("movie:delete_record", args=[self.movie_b.id]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("movie:history", args=[self.user_alice.id]))
        self.assertFalse(Movie_rating.objects.filter(user=self.user_alice, movie=self.movie_b).exists())

    def test_recommend_view_returns_unseen_movies_from_similar_users(self):
        self.login_as_alice()

        response = self.client.get(reverse("movie:recommend"))

        self.assertEqual(response.status_code, 200)
        movies = list(response.context["movies"])
        movie_names = [movie.name for movie in movies]
        self.assertIn("Space Mission", movie_names)
        self.assertIn("Mixed Epic", movie_names)
        self.assertNotIn("Action Hero", movie_names)
        self.assertNotIn("Drama Life", movie_names)
