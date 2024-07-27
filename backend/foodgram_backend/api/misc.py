class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False)
    name = serializers.CharField()
    measurement_unit = serializers.CharField(required=False)
    amount = serializers.SerializerMethodField(read_only=False)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        request = self.context.get('request')
        if request.method == 'GET':
            return obj.amount
        for ingr in request.data.get('ingredients'):
            if ingr['id'] == obj.id:
                return ingr['amount']
        raise serializers.ValidationError('No such ingredient in Recipe!')

    def get_name(self, obj):
        ingredient = get_object_or_404(Ingredient, id=obj.ingredient)
        return ingredient.name

    def get_measurement_unit(self, obj):
        ingredient = get_object_or_404(Ingredient, id=obj.ingredient)
        return ingredient.measurement_unit


    @action(
        methods=['get'], detail=True, url_path='get-link'
    )
    def get_short_link(self, request, pk):
        """Получение короткой ссылки на рецепт"""

        recipe = get_object_or_404(Recipe, pk=pk)
        if not recipe:
            raise ValueError('No recipe to process')
        protocol_host = request.scheme + '://' + request.META.get(
            'HTTP_HOST'
        )
        origin_path = reverse('recipes-detail', args=(pk,))
        origin_url = f'{protocol_host}{origin_path}'
        if UrlMap.objects.filter(full_url=origin_url).exists():
            existing_link = UrlMap.objects.get(full_url=origin_url)
            short_link = f'{protocol_host}/s/{existing_link.short_url}'
            return Response(
                {'short-link': short_link}, status=status.HTTP_200_OK
            )
        if request.user.is_authenticated:
            link = shortener.create(user=request.user, link=origin_url)
        else:
            admin = User.objects.filter(is_staff=True).first()
            link = shortener.create(user=admin, link=origin_url)
        short_link = f'{protocol_host}/s/{link.short_url}'
        return Response(
            {'short-link': short_link}, status=status.HTTP_200_OK
        )

        try:
            tag_list = data['tags']
            for tag in tag_list:
                cur_tag = get_object_or_404(Tag, id=tag)
                tag = {
                    'id': cur_tag.id,
                    'name': cur_tag.name,
                    'slug': cur_tag.slug
                }
            print(tag_list)
            data['tags'] = tag_list
        except KeyError:
            raise serializers.ValidationError('No tag list!')

    def to_representation(self, instance):
        queryset = instance.ingredients.set().all()
        serializer = IngredientAmountSerializer(
            queryset, context={'recipe_id': instance.id}, many=True
        )
        instance.ingredients = serializer.data
        return super().to_representation(instance)