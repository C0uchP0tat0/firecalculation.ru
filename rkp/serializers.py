from dataclasses import fields
from rest_framework import serializers

from .models import FireObject, FireLoad, Quantity


class QuantitySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Quantity
        fields = '__all__'


class FireLoadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FireLoad
        fields = ['material', 'heat']


class FireObjectSerializer(serializers.ModelSerializer):
    
    quantity = QuantitySerializer(read_only=True, many=True)
    
    class Meta:
        model = FireObject
        # fields = '__all__'
        fields = ['title', 'length', 'width', 'height', 'result', 'quantity', 'user']
        # depth = 2
