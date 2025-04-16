from django.db import models

# Wagtail (>=6.4) imports
from wagtail.models import Page, Site
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.images import get_image_model_string
from wagtail.fields import RichTextField

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
    template = "home/home_page.html"
    
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
    

class SectionPage(BasePage):
    """
    Página para secciones estáticas o informativas.
    """
    template = "home/section_page.html"  # Define la plantilla para SectionPage.
    body = RichTextField(blank=True)
    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    subpage_types = []  # Puedes restringir la creación de subpáginas si lo deseas.


class BlogIndexPage(BasePage):
    """
    Página índice que lista las entradas del blog.
    """
    template = "home/blog_index.html"  # Define la plantilla para el índice del blog.
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    # Permite solo páginas de tipo BlogPage como subpáginas.
    subpage_types = ['home.BlogPage']

    def get_context(self, request):
        context = super().get_context(request)
        context['blogpages'] = self.get_children().live().order_by('-first_published_at')
        return context


class BlogPage(BasePage):
    """
    Página individual para cada entrada de blog.
    """
    template = "home/blog_page.html"  # Define la plantilla para las entradas del blog.
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ['home.BlogIndexPage']  # Restricción de creación.