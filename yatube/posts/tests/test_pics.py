import shutil
import tempfile
from django.contrib.auth import get_user_model

from django.utils import timezone
from django.db.models.fields.files import ImageFieldFile

from posts.forms import PostForm
from posts.models import Post
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TaskPagesTests, cls).setUpClass()
        cls.user = User.objects.create_user(username="HasNoName")
        cls.group = Group.objects.create(
            title="Test group",
            slug="test_group_slug",
            description="Test group description",
        )

        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
            pub_date=timezone.now(),
            group=cls.group,
            image=cls.uploaded,
        )

        cls.authorized_client = Client()
        cls.guest_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_detail_pic(self):
        """для post_detail передается правильный контекст с картинкой"""
        print("____context with pic for post_detail_____")

        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )

        obj = response.context["post"]
        self.assertEqual(obj.image, self.post.image)

    def test_index_contains_pic(self):
        """картинка отдается в index"""
        response = self.guest_client.get(reverse("posts:index"))
        obj = response.context.get("page_obj")[0]
        print(f"картинка в индексе {obj}")
        self.assertEqual(obj.image, self.post.image)

    def test_profile_contains_pic(self):
        """картинка отдается в profile"""
        response = self.authorized_client.get(
            reverse(
                "posts:profile",
                kwargs={"username": self.post.author.get_username()},
            )
        )
        obj = response.context.get("page_obj")[0]
        print(f"картинка в profile {obj}")
        self.assertEqual(obj.image, self.post.image)

    def test_group_list_contains_pic(self):
        """картинка отдается в group_list"""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.post.group.slug})
        )
        obj = response.context.get("page_obj")[0]
        print(f"картинка в group_list {obj}")
        self.assertEqual(obj.image, self.post.image)

    def test_form_create_with_pic(self):
        """Тестируем форму с картинкой"""

        print("_____Тестируем форму с картинкой____")
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "group": "Тестовый заголовок",
            "text": "Тестовый текст",
            "image": uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )

        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст", image="posts/small.gif"
            ).exists()
        )
