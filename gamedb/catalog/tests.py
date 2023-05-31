import datetime
from django.core.files import File
from django.test import TestCase, override_settings
from django.test import TestCase, Client
from catalog.models import comments, Profile, Game_List, Game,Company,Genre
from django.utils import timezone
from django.urls import reverse
from catalog.forms import CommentBox, updateForm, ProfileUploader, NewList,RegisterForm,gameSearch, ReviewBox, existingLists
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO, StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import mock

USER_MODEL = get_user_model()

class BaseGameTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseGameTestCase, cls).setUpClass()
        cls.game = Game(game_title='Test Game',summary="Test",genre_list=[4,3],developer_id=1,publisher_id=1,id=1)
        cls.game.save()
        cls.company = Company(company_name="Test Company", company_id=1, published_list=[1],developed_list=[1])
        cls.company.save()
        cls.first_genre = Genre(genre_id=1, genre_name="First Test Genre")
        cls.first_genre.save()
        cls.second_genre = Genre(genre_id=3,genre_name="Second Test Genre")
        cls.second_genre.save()

class GameModelTestCase(BaseGameTestCase):
        def test_game_object_creation(self):
            self.assertEqual(self.game.game_title, 'Test Game')

        def test_absolute_url_game(self):
            self.assertEqual(self.game.get_absolute_url(), reverse('game-description', args=[str(self.game.id)]))
        
        def test_company_object_creation(self):
            self.assertEqual(self.company.company_name, 'Test Company')

        def test_genre_object_creation(self):
            self.assertEqual(self.first_genre.genre_name, 'First Test Genre')


class BaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('change_password')
        cls.user = USER_MODEL.objects.create_user(
            email='test@test.com',
            first_name='Test',
            last_name='User',
            username='user123',
            password='password123'
        )

class PasswordChangeTest(BaseTestCase):
    def test_fail_password_change_request(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_get_password_change(self):

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/change_password.html')

class ProfilePageView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('profile')
        cls.user = USER_MODEL.objects.create_user(
            email='test@test.com',
            first_name='Test',
            last_name='User',
            username='user123',
            password='password123   '
        )
        cls.profile = Profile.objects.create(user=cls.user)

    def test_fail_profile_request(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_get_profile_page(self):

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')

class MyCollectionView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('my_collection')
        cls.user = USER_MODEL.objects.create_user(
            email='test@test.com',
            first_name='Test',
            last_name='User',
            username='user123',
            password='password123   '
        )
        cls.profile = Profile.objects.create(user=cls.user)

    def test_fail_my_collection_request(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_get_my_collection(self):

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/collection.html')

class MyListView(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.url = reverse('my_lists')
        cls.user = USER_MODEL.objects.create_user(
            email='test@test.com',
            first_name='Test',
            last_name='User',
            username='user123',
            password='password123   '
        )
        cls.profile = Profile.objects.create(user=cls.user)

    def test_fail_my_collection_request(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_get_my_collection(self):

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/my_lists.html')

class ProfileUpdateFormTests(TestCase):

    def test_update_my_profile_valid(self):
        testForm = updateForm(data={"email":"john@","username":"user123","first_name":"John","last_name":"Doe"})
        self.assertFalse(testForm.is_valid())

    def test_update_my_profile_valid(self):
        testForm = updateForm(data={"email":"john@test.com","username":"user123","first_name":"John","last_name":"Doe"})
        self.assertTrue(testForm.is_valid())

class ProfileUpdateFormTests(TestCase):

    def test_update_my_profile_invalid(self):
        testForm = updateForm(data={"email":"john@","username":"user123","first_name":"John","last_name":"Doe"})
        self.assertFalse(testForm.is_valid())

    def test_update_my_profile_valid(self):
        testForm = updateForm(data={"email":"john@test.com","username":"user123","first_name":"John","last_name":"Doe"})
        self.assertTrue(testForm.is_valid())

class ProfilePictureFormTests(TestCase):

    def test_update_my_profile_picture_valid(self):
        mock_file = mock.MagicMock(spec=File)
        mock_file.name = 'test.pdf'
        testForm = ProfileUploader(files={"profile_pic":mock_file})
        self.assertTrue(testForm.is_valid())

class CreateNewListTests(TestCase):

    def test_update_my_profile_picture_valid(self):
        mock_file = mock.MagicMock(spec=File)
        mock_file.name = 'test.pdf'
        testForm = NewList(data={"title":"test","blurb":"test"},files={"hero_image":mock_file})
        self.assertTrue(testForm.is_valid())

class CommentForm(TestCase):

    def test_post_comment(self):
        testComment = CommentBox(data={"title":"test","comment":"test"})
        self.assertTrue(testComment.is_valid())

class TestRegistrationForm(TestCase):

    def test_registration_form_is_valid(self):
        testRegister = RegisterForm(data={"username":"JohnBoy","email":"test@test.com","password1":"Password456","password2":"Password456"})
        self.assertTrue(testRegister.is_valid())

    def test_registration_form_is_invalid(self):
        testRegister = RegisterForm(data={"username":"JohnBoy","email":"test@test.com","password1":"password123","password2":"password123"})
        self.assertFalse(testRegister.is_valid())

class GameSearch(TestCase):

    def test_game_search_is_valid(self):
        testSearch = gameSearch(data={"search_query":"Test"})
        self.assertTrue(testSearch.is_valid())
    
class TestReviewForm(TestCase):

    def test_review_form_is_valid(self):       
        testReview = ReviewBox(data={"title":"test", "Review":5,"comment":"test"})
        self.assertTrue(testReview.is_valid())

class ConfirmErrorResponse(TestCase):
    def test_404_error_response(self):
        response = self.client.get('/catalog/doesnotexist/')
        self.assertEqual(response.status_code, 404)

class TestURLs(TestCase):
    def test_index(self):
        index_url = reverse('index')
        self.assertEqual(index_url, '/catalog/')

    def test_developer_items(self):
        developer_items_url = reverse('developer_items',args=[25])
        self.assertEqual(developer_items_url, '/catalog/developers/25')
    
    def test_publisher_items(self):
        publisher_items_url = reverse('publisher_items',args=[25])
        self.assertEqual(publisher_items_url, '/catalog/publishers/25')
    
    def test_review_submission(self):
        submit_review_url = reverse('submit_review',args=[25])
        self.assertEqual(submit_review_url, '/catalog/submit_review/25')
    
    def test_comment_submission(self):
        submit_comment_url = reverse('submit_comment',args=[25])
        self.assertEqual(submit_comment_url, '/catalog/submit_comment/25')

    def test_edit_list(self):
        edit_list_url = reverse('edit_list',args=[25])
        self.assertEqual(edit_list_url, '/catalog/lists/edit_list/25')

    def test_registration(self):
        registration_url = reverse('register')
        self.assertEqual(registration_url, '/catalog/register')

    def test_add_button(self):
        add_button_url = reverse('add_button')
        self.assertEqual(add_button_url, '/catalog/add_button')

    def test_account_profile(self):
        account_profile_url = reverse('profile')
        self.assertEqual(account_profile_url, '/catalog/accounts/profile')

    def test_my_collection(self):
        my_collection_url = reverse('my_collection')
        self.assertEqual(my_collection_url, '/catalog/accounts/profile/my_collection')

    def test_genres(self):
        genres_url = reverse('genre_list')
        self.assertEqual(genres_url, '/catalog/genres/all_genres')

    def test_developers(self):
        developers_url = reverse('all_developers')
        self.assertEqual(developers_url, '/catalog/developers/all_developers')

    def test_publishers(self):
        publishers_url = reverse('all_publishers')
        self.assertEqual(publishers_url, '/catalog/publishers/all_publishers')

    def test_my_lists(self):
        my_lists_url = reverse('my_lists')
        self.assertEqual(my_lists_url, '/catalog/accounts/profile/my_lists')

    def test_publish_list(self):
        publish_list_url = reverse('publish_list')
        self.assertEqual(publish_list_url, '/catalog/accounts/profile/publish_list')

    def test_unpublish_list(self):
        unpublish_list_url = reverse('unpublish_list')
        self.assertEqual(unpublish_list_url, '/catalog/accounts/profile/unpublish_list')

    def test_create_list(self):
        create_list_url = reverse('create_list')
        self.assertEqual(create_list_url, '/catalog/accounts/profile/create_list')

    def test_add_to_list(self):
        add_to_list_url = reverse('add_to_list')
        self.assertEqual(add_to_list_url, '/catalog/add_to_list')

    def test_remove_from_list(self):
        remove_from_list_url = reverse('remove_from_list')
        self.assertEqual(remove_from_list_url, '/catalog/remove_from_list')

    def test_all_lists(self):
        all_lists_url = reverse('all_lists')
        self.assertEqual(all_lists_url, '/catalog/all_lists')