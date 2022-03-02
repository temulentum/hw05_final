from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import Group, Post

User = get_user_model()


class TaskURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="HasNoName")
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
            pub_date=timezone.now(),
            group=Group.objects.create(
                title="Test group",
                slug="test_group_slug",
                description="Test group description",
            ),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_create_exists_for_authorized(self):
        """Проверяем, что авторизованному пользователю
        доступна страница создания поста"""
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, 200, "Не могу написать пост")

    def test_url_create_redirects_unauthorized(self):
        """Проверяем, что неавторизованный юзер перенаправляется
        вместо стр.создания поста на форму логина"""
        response = self.guest_client.get("/create/")
        self.assertRedirects(response, "/auth/login/?next=/create/")

    def test_url_post_edit_exists_for_authorized(self):
        """Проверяем, что авторизованному юзеру
        доступно редактирование своих постов"""
        response = self.authorized_client.get(f"/posts/{self.post.id}/edit/")
        self.assertEqual(
            response.status_code, 200, "Не могу отредактировать пост"
        )

    def test_url_edit_redirects_unauthorized(self):
        """Проверяем, что нельзя редактировать чужие
        посты - редирект на страницу поста"""
        response = self.guest_client.get(f"/posts/{self.post.id}/edit/")
        self.assertRedirects(response, f"/posts/{self.post.id}/")

    def test_urls_exist_for_guest(self):
        """Проверяем доступность страниц для всех юзеров"""
        urls_response_codes = {
            "/": 200,
            "/group/test_group_slug/": 200,
            "/profile/HasNoName/": 200,
            "/unexisting_page/": 404,
        }
        for adress, code in urls_response_codes.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(
                    response.status_code,
                    code,
                    f"Страница {adress} работает неправильно или недоступна",
                )

    def test_urls_uses_correct_templates(self):
        """Проверяем urls.py на корректное использование шаблонов"""
        urls_templates = {
            "/": "posts/index.html",
            "/group/" + self.post.group.slug + "/": "posts/group_list.html",
            "/profile/" + self.user.username + "/": "posts/profile.html",
            "/posts/" + str(self.post.id) + "/": "posts/post_detail.html",
            "/posts/" + str(self.post.id) + "/edit/": "posts/create_post.html",
        }
        for adress, template_page in urls_templates.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                print(f"----url----: {adress}")
                self.assertTemplateUsed(response, template_page)

    def test_404_uses_custom_template(self):
        """Кастомный шаблон на 404?"""
        response = self.guest_client.get("/unexisting_page/")
        self.assertTemplateUsed(response, "core/404.html")
