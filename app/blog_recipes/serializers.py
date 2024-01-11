"""
serializers for blog recipeapi
"""

from rest_framework import serializers

from core.models import (
    BlogRecipe,
    BlogIngredient,
    BlogNote,
    BlogInstruction,
    BlogAuthor,
    BlogImage,
)


class BlogIngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient object"""
    class Meta:
        """Meta class"""
        model = BlogIngredient
        fields = ('ingredient',)


class BlogNoteSerializer(serializers.ModelSerializer):
    """Serializer for note object"""
    class Meta:
        """Meta class"""
        model = BlogNote
        fields = ('note',)


class BlogInstructionSerializer(serializers.ModelSerializer):
    """Serializer for instruction object"""
    class Meta:
        """Meta class"""
        model = BlogInstruction
        fields = ('instruction',)


class BlogAuthorSerializer(serializers.ModelSerializer):
    """Serializer for author object"""
    # recipes = BlogRecipeSerializer(many=True, read_only=True)

    class Meta:
        """Meta class"""
        model = BlogAuthor
        fields = ('id', 'name', 'website_link')
        read_only_fields = ('id',)


class BlogRecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""
    author = BlogAuthorSerializer(read_only=True)

    class Meta:
        """Meta class"""
        model = BlogRecipe
        fields = (
            "id", "title", "link", "rating", "category", "author", "slug",
        )
        read_only_fields = ('id',)


class BlogRecipeImageSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading images to recipes
    """
    class Meta:
        """Meta class"""
        model = BlogImage
        fields = ("id", "image")
        read_only_fields = ("id",)
        extra_kwargs = {
            "image": {
                "required": True,
            }
        }


class BlogRecipeDetailSerializer(BlogRecipeSerializer):
    """
    Serializer for recipe detail object
    """
    ingredients = serializers.SerializerMethodField()
    instructions = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta(BlogRecipeSerializer.Meta):
        """Meta class"""
        fields = BlogRecipeSerializer.Meta.fields + (
            "description", "num_reviews", "prep_time", "cook_time",
            "total_time", "servings", "images",
            "ingredients", "instructions", "notes"
        )
        read_only_fields = ('id',)

    def get_ingredients(self, obj):
        """orders ingredients by id to preserve original order"""
        ordered_ingredients = obj.ingredients.order_by('id')
        return [ingredient['ingredient']
                for ingredient in ordered_ingredients.values()]

    def get_instructions(self, obj):
        """orders instructions by id to preserve original order"""
        ordered_instructions = obj.instructions.order_by('id')
        return [instruction['instruction']
                for instruction in ordered_instructions.values()]

    def get_notes(self, obj):
        """orders notes by id to preserve original order"""
        ordered_notes = obj.notes.order_by('id')
        return [note['note'] for note in ordered_notes.values()]

    def get_images(self, obj):
        """orders images by id to preserve original order"""
        ordered_images = obj.images.order_by('id')
        return [image['image'] for image in ordered_images.values()]
