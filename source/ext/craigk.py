from __future__ import annotations

from docutils import nodes

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective, SphinxRole
from sphinx.util.typing import ExtensionMetadata

class IntroductionDirective(SphinxDirective):
    required_arguments = 1

    def run(self) -> list[nodes.Node]:
        paragraph_node = nodes.paragraph(text=f'{self.arguments[0]}')
        return [paragraph_node]
    
class ProfessionalExperienceDirective(SphinxDirective):
    required_arguments = 1

    def run(self) -> list[nodes.Node]:
        paragraph_node = nodes.paragraph(text=f'{self.arguments[0]}')
        return [paragraph_node]

def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive('introduction', IntroductionDirective)
    app.add_directive('professional_experience', ProfessionalExperienceDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }