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
    BlogCategory,
    BlogIngredientList,
)


class BlogIngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient object"""
    class Meta:
        """Meta class"""
        model = BlogIngredient
        fields = ('ingredient',)


class BlogIngredientListSerializer(serializers.ModelSerializer):
    """Serializer for ingredient list object"""
    ingredients = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""
        model = BlogIngredientList
        fields = ('title', 'ingredients')

    def get_ingredients(self, obj):
        """orders ingredients by id to preserve original order"""
        ordered_ingredients = obj.ingredients.order_by('id')
        return [ingredient['ingredient']
                for ingredient in ordered_ingredients.values()]


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


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for category object"""
    class Meta:
        """Meta class"""
        model = BlogCategory
        fields = ('id', "name")
        read_only_fields = ('id',)


class BlogAuthorSerializer(serializers.ModelSerializer):
    """Serializer for author object"""
    categories = serializers.SerializerMethodField()
    total_recipes = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""
        model = BlogAuthor
        fields = ('id', 'name', 'website_link', "total_recipes", 'categories')
        read_only_fields = ('id',)

    def get_categories(self, obj):
        """orders ingredients by id to preserve original order"""
        ordered_categories = obj.categories.order_by('id')
        return [category['name']
                for category in ordered_categories.values()]

    def get_total_recipes(self, obj):
        """Get the total number of recipes by the author"""
        return obj.recipes.count()


class BlogRecipeImageSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading images to recipes
    """
    class Meta:
        """Meta class"""
        model = BlogImage
        fields = ("image_url", "name")
        read_only_fields = ("id",)


class BlogRecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""
    author = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()

    class Meta:
        """Meta class"""
        model = BlogRecipe
        fields = (
            "id", "title", "categories", "link",
            "rating", "author", "slug", "main_image"
        )
        read_only_fields = ('id',)

    def get_author(self, obj):
        """gets author name only"""
        return obj.author.name

    def get_categories(self, obj):
        """orders categories by id to preserve original order"""
        ordered_categories = obj.categories.order_by('id')
        return [category['name']
                for category in ordered_categories.values()]

    def get_main_image(self, obj):  # Add this method
        """Return only the first image"""
        images = obj.images
        request = self.context.get('request')
        # get the host name
        host = request.build_absolute_uri() \
            .split('/')[0] + '//' + \
            request.build_absolute_uri().split('/')[2]
        if images.exists():
            first_image = images.last().image_url.url
            print(host + first_image)
            return host + first_image
        else:
            return None


class BlogRecipeDetailSerializer(BlogRecipeSerializer):
    """
    Serializer for recipe detail object
    """
    ingredient_list = BlogIngredientListSerializer(many=True, read_only=True)
    instructions = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    images = BlogRecipeImageSerializer(many=True, read_only=True)

    class Meta(BlogRecipeSerializer.Meta):
        """Meta class"""
        fields = BlogRecipeSerializer.Meta.fields + (
            "description", "num_reviews", "prep_time", "cook_time",
            "total_time", "servings", "images",
            "ingredient_list", "instructions", "notes"
        )
        read_only_fields = ('id',)

    def get_instructions(self, obj):
        """orders instructions by id to preserve original order"""
        ordered_instructions = obj.instructions.order_by('id')
        return [instruction['instruction']
                for instruction in ordered_instructions.values()]

    def get_notes(self, obj):
        """orders notes by id to preserve original order"""
        ordered_notes = obj.notes.order_by('id')
        return [note['note'] for note in ordered_notes.values()]
