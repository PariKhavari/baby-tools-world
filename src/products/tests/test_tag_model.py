from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from btw_app.utils import log_execution
from products.models import Category, Product, Tag


class TagModelTest(TestCase):
    """Tests for the Tag model fields and basic creation."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up test data once for all tests in this class."""
        cls.tag = Tag.objects.create(name="Baby Toys")
        cls.category = Category.objects.create(name="Test Category", slug="test-category")
        cls.product = Product.objects.create(
            name="Wooden Rattle",
            description="A nice wooden rattle.",
            price="12.99",
            category=cls.category,
        )

    @log_execution
    def test_tag_is_created_successfully(self) -> None:
        """Test that a Tag instance can be created and saved to the database."""
        tag = Tag.objects.create(name="Safety Gear")
        tag.full_clean()
        self.assertIsNotNone(tag.id)
        self.assertEqual(tag.name, "Safety Gear")

    @log_execution
    def test_tag_name_field(self) -> None:
        """Test that the name field stores and returns the correct value."""
        self.assertEqual(self.tag.name, "Baby Toys")

    @log_execution
    def test_tag_id_is_auto_assigned(self) -> None:
        """Test that Django automatically assigns an integer id to a new Tag."""
        self.assertIsNotNone(self.tag.id)
        self.assertIsInstance(self.tag.id, int)

    @log_execution
    def test_tag_created_at_is_set_automatically(self) -> None:
        """Test that created_at is populated automatically on creation."""
        self.assertIsNotNone(self.tag.created_at)
        self.assertLessEqual(self.tag.created_at, timezone.now())

    @log_execution
    def test_tag_updated_at_is_set_automatically(self) -> None:
        """Test that updated_at is populated automatically on creation."""
        self.assertIsNotNone(self.tag.updated_at)
        self.assertLessEqual(self.tag.updated_at, timezone.now())

    @log_execution
    def test_tag_updated_at_changes_on_save(self) -> None:
        """Test that updated_at is refreshed whenever the Tag is saved."""
        tag = Tag.objects.create(name="Temporary Tag")
        original_updated_at = tag.updated_at
        tag.name = "Updated Tag Name"
        tag.save()
        tag.refresh_from_db()
        self.assertGreaterEqual(tag.updated_at, original_updated_at)

    @log_execution
    def test_created_at_does_not_change_on_save(self) -> None:
        """Test that created_at remains unchanged after subsequent saves."""
        tag = Tag.objects.create(name="Stable Tag")
        original_created_at = tag.created_at
        tag.name = "Modified Name"
        tag.save()
        tag.refresh_from_db()
        self.assertEqual(tag.created_at, original_created_at)

    @log_execution
    def test_tag_string_representation(self) -> None:
        """Test the string representation of a Tag returns its name."""
        self.assertEqual(str(self.tag), "Baby Toys")

    @log_execution
    def test_failure_tag_creation_without_name(self) -> None:
        """Test that a Tag cannot be created with a blank name."""
        with self.assertRaises(ValidationError) as ctx:
            tag = Tag(name="")
            tag.full_clean()
        self.assertEqual(ctx.exception.message_dict, {"name": ["This field cannot be blank."]})


class TagProductRelationTest(TestCase):
    """Tests for the ManyToMany relationship between Tag and Product."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Set up a product and two tags for relationship tests."""
        cls.category = Category.objects.create(name="Test Category", slug="test-category")
        cls.product = Product.objects.create(
            name="Wooden Rattle",
            description="A nice wooden rattle.",
            price="12.99",
            category=cls.category,
        )
        cls.tag_one = Tag.objects.create(name="Baby Toys")
        cls.tag_two = Tag.objects.create(name="Wooden")

    @log_execution
    def test_tag_can_be_assigned_to_product(self) -> None:
        """Test that a single tag can be added to a product."""
        self.product.tags.add(self.tag_one)
        self.assertIn(self.tag_one, self.product.tags.all())

    @log_execution
    def test_multiple_tags_can_be_assigned_to_product(self) -> None:
        """Test that multiple tags can be added to a single product."""
        self.product.tags.add(self.tag_one, self.tag_two)
        self.assertEqual(self.product.tags.count(), 2)
        self.assertIn(self.tag_one, self.product.tags.all())
        self.assertIn(self.tag_two, self.product.tags.all())

    @log_execution
    def test_product_without_tags_has_empty_tag_set(self) -> None:
        """Test that a product with no tags assigned has an empty tags queryset."""
        product = Product.objects.create(
            name="Untagged Product",
            description="A product with no tags.",
            price="5.99",
            category=self.category,
        )
        self.assertEqual(product.tags.count(), 0)

    @log_execution
    def test_tag_can_be_removed_from_product(self) -> None:
        """Test that a tag can be removed from a product."""
        self.product.tags.add(self.tag_one)
        self.product.tags.remove(self.tag_one)
        self.assertNotIn(self.tag_one, self.product.tags.all())

    @log_execution
    def test_one_tag_can_belong_to_multiple_products(self) -> None:
        """Test that a single tag can be assigned to more than one product."""
        second_product = Product.objects.create(
            name="Soft Ball",
            description="A soft rubber ball.",
            price="7.49",
            category=self.category,
        )
        self.product.tags.add(self.tag_one)
        second_product.tags.add(self.tag_one)
        self.assertIn(self.tag_one, self.product.tags.all())
        self.assertIn(self.tag_one, second_product.tags.all())
