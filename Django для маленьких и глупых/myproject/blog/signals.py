# blog/signals.py
from django.db.models.signals import m2m_changed, pre_save
from django.dispatch import receiver
from taggit.models import Tag
from .models import Post
import pytils
from django.utils.text import slugify


@receiver(pre_save, sender=Tag)
def update_tag_slug(sender, instance, **kwargs):
    """Для ручного создания тегов с уникальностью"""
    if instance.name:
        transliterated = pytils.translit.translify(instance.name)
        base_slug = slugify(transliterated)

        # Проверяем уникальность slug
        new_slug = base_slug
        counter = 1

        # Ищем уникальный slug
        while Tag.objects.filter(slug=new_slug).exclude(id=instance.id).exists():
            new_slug = f"{base_slug}-{counter}"
            counter += 1

        instance.slug = new_slug


@receiver(m2m_changed, sender=Post.tags.through)
def update_tags_on_post_save(sender, instance, action, **kwargs):
    """При сохранении поста с тегами"""
    if action == "post_add":
        for tag in instance.tags.all():
            # Проверяем содержит ли slug кириллицу
            has_cyrillic = any('а' <= c <= 'я' for c in (tag.slug or ''))

            if has_cyrillic or not tag.slug:
                transliterated = pytils.translit.translify(tag.name)
                base_slug = slugify(transliterated)

                # Проверяем уникальность
                new_slug = base_slug
                counter = 1

                while Tag.objects.filter(slug=new_slug).exclude(id=tag.id).exists():
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1

                tag.slug = new_slug
                tag.save()