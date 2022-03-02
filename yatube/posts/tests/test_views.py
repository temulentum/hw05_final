from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Post, Group
from ..forms import PostForm

User = get_user_model()


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
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый текст",
            pub_date=timezone.now(),
            group=cls.group,
        )

        cls.authorized_client = Client()
        cls.guest_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_pages_uses_correct_template(self):
        """Проверяем корректное использование шаблонов view-функциями"""
        templates_and_url_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": self.post.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": self.user.get_username()}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.id}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for name, template in templates_and_url_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                print(f"Тестируем шаблон для view ---- {name} ----")
                self.assertTemplateUsed(response, template)

    def test_index_context_is_posts_list(self):
        """На главную страницу передаётся спиcок постов
        (Объект Paginator.page)"""
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(
            len(response.context.get("page_obj")), 1, "Не похоже на список!"
        )

    def test_group_list_recieves_list_filterd_by_group(self):
        """group_list доллжен содержать список постов,
        отфильтрованных по группе"""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        self.assertEqual(
            response.context.get("group"), self.group, "Группа не совпала"
        )

    def test_profile_recieves_posts_filterd_by_author(self):
        """profile должен получать список постов, отфильтрованный по автору"""
        response = self.guest_client.get(
            reverse(
                "posts:profile", kwargs={"username": self.user.get_username()}
            )
        )
        self.assertEqual(
            response.context.get("author"), self.user, "Автор не совпал"
        )

    def test_post_detail_has_1_post_selected_by_id(self):
        """post_detail должна содержать 1 пост, отобранный по id"""
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(
            response.context.get("post").id,
            self.post.id,
            "post_detail работает неправильно.",
        )

    def test_post_edit_has_form_with_post(self):
        """post_edit должен получать форму с постом, отобранным по id"""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(
            response.context.get("post_id"),
            self.post.id,
            "Редактирование поста работает неправильно",
        )

    def test_post_create_has_form(self):
        """post_create должен получать форму создания поста"""
        response = self.authorized_client.get(reverse("posts:post_create"))
        self.assertTrue(
            isinstance(response.context.get("form"), PostForm),
            "Форма какая-то не та",
        )

    def test_group_hasnt_alien_posts(self):
        """Созданный пост не должен попасть в чужую группу"""
        Group.objects.create(
            title="Another group",
            slug="another_group_slug",
            description="another group description",
        )
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "another_group_slug"})
        )
        another_group_post_list = response.context.get("page_obj").object_list
        self.assertFalse(self.post in another_group_post_list)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PaginatorViewsTest, cls).setUpClass()
        cls.user = User.objects.create_user(username="HasNoName")
        cls.group = Group.objects.create(
            title="Test group",
            slug="test_group_slug",
            description="Test group description",
        )
        cnt = 1
        while cnt <= 13:
            Post.objects.create(
                author=cls.user,
                text="Тестовый текст" + str(cnt),
                pub_date=timezone.now(),
                group=cls.group,
            )
            cnt += 1
        cls.guest_client = Client()

    def test_first_page_contains_ten_records(self):
        """Paginator | index: На первой странице 10 постов"""
        response = self.guest_client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_second_page_contains_three_records(self):
        """Paginator  |  index: на второй странице 3 поста"""
        response = self.guest_client.get(reverse("posts:index") + "?page=2")
        self.assertEqual(len(response.context["page_obj"]), 3)

    def test_group_list_contains_ten_records(self):
        """Paginator  |  group_list: На первой странице 10 постов"""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
        )
        self.assertEqual(len(response.context["page_obj"]), 10, "Не десять!")

    def test_group_list_second_page_contains_three_records(self):
        """Paginator  |  group_list: На второй странице 3 поста"""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": self.group.slug})
            + "?page=2"
        )
        self.assertEqual(len(response.context["page_obj"]), 3, "Не три!")
