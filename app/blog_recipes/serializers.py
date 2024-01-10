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
        fields = ('id', 'ingredient')
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
        fields = ('id', 'name', 'website_link')
        read_only_fields = ('id',)


class BlogRecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes"""
    # ingredients = IngredientSerializer(many=True, required=False)
    # notes = NoteSerializer(many=True, required=False)
    # instructions = InstructionSerializer(many=True, required=False)
    # author = AuthorSerializer(many=True, required=True)

    class Meta:
        model = BlogRecipe
        fields = (
            "id", "title", "link", "rating", "category", "author", "slug",
        )
        read_only_fields = ('id',)

# these might not need to get the author, because all recipeswiil be public.
# I dont need to lock down the author like I do with the recipe app.
# this could maybe save space in the db,
# (but unlikely because very specific strings.)

    # def _get_or_create_notes(self, notes_to_add, recipe):
    #     """handle getting or creating notes"""
    #     author = self.context["request"].author
    #     for note in notes_to_add:
    #         note_obj, create = BlogNote.objects.get_or_create(
    #             author=author,
    #             **note
    #         )
    #         recipe.notes.add(note_obj)

    # def _get_or_create_instructions(self, instructions_to_add, recipe):
    #     """handle getting or creating instructions"""
    #     author = self.context["request"].author
    #     for instruction in instructions_to_add:
    #         instruction_obj, create = BlogInstruction.objects.get_or_create(
    #             author=author,
    #             **instruction
    #         )
    #         recipe.instructions.add(instruction_obj)

    # def _get_or_create_ingredients(self, ingredients_to_add, recipe):
    #     """handle getting or creating ingredients"""
    #     author = self.context["request"].author
    #     for ingredient in ingredients_to_add:
    #         ing_obj, create = BlogIngredient.objects.get_or_create(
    #             author=author,
    #             **ingredient
    #         )
    #         recipe.ingredients.add(ing_obj)

    def create(self, validated_data):
        """Create a recipe"""
        ingredients = validated_data.pop('ingredients', [])
        notes = validated_data.pop('notes', [])
        instructions = validated_data.pop('instructions', [])
        # authors = validated_data.pop('authors', [])
        recipe = BlogRecipe.objects.create(**validated_data)
        self.get_or_create_ingredients(ingredients, recipe)
        self.get_or_create_notes(notes, recipe)
        self.get_or_create_instructions(instructions, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        self._get_or_create_notes(notes, recipe)
        self._get_or_create_instructions(instructions, recipe)
        # self._get_or_create_authors(authors, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe"""
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            self.get_or_create_ingredients(ingredients, instance)

        notes = validated_data.pop('notes', None)
        if notes is not None:
            instance.notes.clear()
            self.get_or_create_notes(notes, instance)

        instructions = validated_data.pop('instructions', None)
        if instructions is not None:
            instance.instructions.clear()
            self.get_or_create_instructions(instructions, instance)

        authors = validated_data.pop('authors', None)
        if authors is not None:
            instance.authors.clear()
            self._get_or_create_authors(authors, instance)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class BlogRecipeDetailSerializer(BlogRecipeSerializer):
    """
    Serializer for recipe detail object
    """
    ingredients = BlogIngredientSerializer(many=True, required=False)
    notes = BlogNoteSerializer(many=True, required=False)
    instructions = BlogInstructionSerializer(many=True, required=False)

    class Meta(BlogRecipeSerializer.Meta):
        fields = BlogRecipeSerializer.Meta.fields + (
            "description", "num_reviews", "prep_time", "cook_time",
            "total_time", "servings", "ingredients", "instructions", "notes"
        )

        read_only_fields = ('id',)

    def create(self, validated_data):
        """Create a recipe"""
        ingredients = validated_data.pop('ingredients', [])
        notes = validated_data.pop('notes', [])
        instructions = validated_data.pop('instructions', [])

        recipe = BlogRecipe.objects.create(**validated_data)
        self.get_or_create_ingredients(ingredients, recipe)
        self.get_or_create_notes(notes, recipe)
        self.get_or_create_instructions(instructions, recipe)

        return recipe

    def update(self, instance, validated_data):
        """Update a recipe"""
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()
            self.get_or_create_ingredients(ingredients, instance)

        notes = validated_data.pop('notes', None)
        if notes is not None:
            instance.notes.clear()
            self.get_or_create_notes(notes, instance)

        instructions = validated_data.pop('instructions', None)
        if instructions is not None:
            instance.instructions.clear()
            self.get_or_create_instructions(instructions, instance)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance
