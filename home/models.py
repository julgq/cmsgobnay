from django.db import models

# Wagtail (>=6.4) imports
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.images import get_image_model_string
from wagtail.models import Site

############################################
#          SITE SETTINGS (Wagtail 6.4+)
############################################


@register_setting
class SiteBrandingSettings(BaseSiteSetting):
    
    """
    Ajustes específicos para cada 'Site' (dominio/subdominio).
    Wagtail detectará automáticamente si el campo apunta
    a una imagen y mostrará un chooser de imágenes en el panel.
    """



    site_logo = models.ForeignKey(
        get_image_model_string(),  # Apunta a la tabla de Wagtail Images
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Logo principal para este sitio."
    )

    panels = [
        # Ya NO es necesario un "ImageChooserPanel" ni "ChooserPanel".
        # Con FieldPanel, Wagtail ve que tu campo es ForeignKey a 'wagtailimages.Image'
        # y muestra el widget de selección de imágenes.
        FieldPanel("site_logo"),
    ]


############################################
#                PÁGINAS
############################################

class BasePage(Page):
    """
    Clase base abstracta para compartir configuración/campos comunes
    en todas tus páginas. 'abstract = True' => No se crea tabla.
    """
    class Meta:
        abstract = True

    # Si quisieras campos comunes a todas las páginas, por ejemplo:
    # intro = models.CharField(max_length=250, blank=True)
    #
    # content_panels = Page.content_panels + [
    #     FieldPanel("intro"),
    # ]


class HomePage(BasePage):
    """
    Página de inicio, hereda de BasePage. 
    Agrega aquí campos específicos de la portada, si los necesitas.
    """
    # Ejemplo:
    # subtitle = models.CharField(max_length=200, blank=True, null=True)
    #
    # content_panels = BasePage.content_panels + [
    #     FieldPanel("subtitle"),
    # ]
    def serve(self, request, *args, **kwargs):
        # Obtén el site según la cabecera Host:
        found_site = Site.find_for_request(request)
        print("DEBUG: found_site =>", found_site.hostname, found_site.port)

        # Revisa qué branding está configurado
        branding = SiteBrandingSettings.for_site(found_site)
        print("DEBUG: branding =>", branding.site_logo)

        return super().serve(request, *args, **kwargs)