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