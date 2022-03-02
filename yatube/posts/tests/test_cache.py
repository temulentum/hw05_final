from posts.models import Post, Group
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
        cls.user = User.objects.create_user(username="HasNoName")
        cls.group = Group.objects.create(
            title="Test group",
            slug="test_group_slug",
            description="Test group description",
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
            pub_date=timezone.now(),
            group=cls.group,
        )

        cls.guest_client = Client()

    def test_no_renewal_while_delay(self):
        """Кэш существует?"""
        content_before = self.guest_client.get(reverse("posts:index")).content
        Post.objects.get(id=self.post.id).delete()
        content_after = self.guest_client.get(reverse("posts:index")).content
        self.assertEqual(content_before, content_after)

    def test_renovation_after_cache_deletion(self):
        """Удаляем кэш, обновляется?"""
        content_before = self.guest_client.get(reverse("posts:index")).content
        cache.clear()
        content_after = self.guest_client.get(reverse("posts:index")).content
        self.assertEqual(content_before, content_after)
