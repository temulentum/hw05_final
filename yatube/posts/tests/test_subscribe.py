from itertools import count
from posts.models import Post, Group, Follow
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache


User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(CacheTests, cls).setUpClass()
        cls.author = User.objects.create_user(username="HasNoName")
        cls.follower = User.objects.create_user(username="Follower")

        cls.group = Group.objects.create(
            title="Test group",
            slug="test_group_slug",
            description="Test group description",
        )

        cls.post_followed = Post.objects.create(
            author=cls.author,
            text="Тестовый текст. Меня читают!",
            pub_date=timezone.now(),
            group=cls.group,
        )

        cls.post_unfollowed = Post.objects.create(
            author=cls.follower,
            text="Тестовый текст. Меня никто не любит!",
            pub_date=timezone.now(),
            group=cls.group,
        )

        cls.follow = Follow.objects.create(
            user=cls.follower, author=cls.author
        )

        cls.guest_client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower)

    def test_authorized_can_subscribe(self):
        """Авторизованному пользователю доступна подписка?"""
        response = self.author_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.follower.get_username()},
            )
        )
        self.assertEqual(response.status_code, 302)

    def test_authorized_can_create_follow_obj(self):
        """Объект Follow создается??"""
        if Follow.objects.filter(
            user=self.author, author=self.follower
        ).exists():
            Follow.objects.filter(
                user=self.author, author=self.follower
            ).delete()

        self.author_client.get(
            reverse(
                "posts:profile_follow",
                kwargs={"username": self.follower.get_username()},
            )
        )

        if Follow.objects.filter(
            user=self.author, author=self.follower
        ).exists():
            follow = True
        print(f"________________________ {follow}")
        self.assertTrue(follow)

    def test_authorized_can_unsubscribe(self):
        """Объект Follow уничтожается??"""
        if not Follow.objects.filter(
            user=self.author, author=self.follower
        ).exists():
            Follow.objects.create(user=self.author, author=self.follower)

        self.author_client.get(
            reverse(
                "posts:profile_unfollow",
                kwargs={"username": self.follower.get_username()},
            )
        )

        if not Follow.objects.filter(
            user=self.author, author=self.follower
        ).exists():
            follow = True
        print(f"________________________ {follow}")
        self.assertTrue(follow)

    def test_new_post_in_followers_feed(self):
        """Фолловеры видят посты любимых авторов"""
        response = self.follower_client.get(reverse("posts:follow_index"))
        post = response.context.get("page_obj")[0]
        self.assertEqual(post.text, "Тестовый текст. Меня читают!")

    def test_none_followers_dont_see_posts(self):
        """Не-фолловеры не видят посты нелюбимых авторов"""
        response = self.author_client.get(reverse("posts:follow_index"))
        obj = len(response.context.get("page_obj").object_list)
        self.assertEqual(0, obj)
