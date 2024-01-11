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
)


class BlogIngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient object"""
    class Meta:
        model = BlogIngredient
        fields = ('id', 'ingredient',)
        read_only_fields = ('id',)


class BlogNoteSerializer(serializers.ModelSerializer):
    """Serializer for note object"""
    class Meta:
        model = BlogNote
        fields = ('id', 'note')
        read_only_fields = ('id',)


class BlogInstructionSerializer(serializers.ModelSerializer):
    """Serializer for instruction object"""
    class Meta:
        model = BlogInstruction
        fields = ('id', 'instruction')
        read_only_fields = ('id',)


class BlogAuthorSerializer(serializers.ModelSerializer):
    """Serializer for author object"""
    class Meta:
        model = BlogAuthor
        fields = ('id', 'name', 'website_link', "recipes")
        read_only_fields = ('id',)


class BlogRecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""

    class Meta:
        model = BlogRecipe
        fields = (
            "id", "title", "link", "rating", "category", "author", "slug",
        )
        read_only_fields = ('id',)


class BlogRecipeDetailSerializer(BlogRecipeSerializer):
    """
    Serializer for recipe detail object
    """
    ingredients = BlogIngredientSerializer(many=True)
    notes = BlogNoteSerializer(many=True, required=False)
    instructions = BlogInstructionSerializer(many=True, required=False)

    class Meta(BlogRecipeSerializer.Meta):
        fields = BlogRecipeSerializer.Meta.fields + (
            "description", "num_reviews", "prep_time", "cook_time",
            "total_time", "servings", "ingredients", "instructions", "notes"
        )

        read_only_fields = ('id',)
