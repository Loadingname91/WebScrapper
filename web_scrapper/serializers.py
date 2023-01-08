from rest_framework import serializers

from .models import ProductResources, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductResourcesSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = ProductResources
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('product'):
            raise serializers.ValidationError("product details are missing")
        return attrs

    def create(self, validated_data):
        product = validated_data.pop('product')
        product_serializer = ProductSerializer(data=product)
        if product_serializer.is_valid():
            product_serializer.save()
            validated_data['product'] = product_serializer.instance
            return super(ProductResourcesSerializer, self).create(validated_data)