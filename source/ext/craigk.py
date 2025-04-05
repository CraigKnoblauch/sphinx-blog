from __future__ import annotations

from docutils import nodes

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective, SphinxRole
from sphinx.util.typing import ExtensionMetadata

class IntroductionDirective(SphinxDirective):
    has_content = True

    def run(self) -> list[nodes.Node]:
        print(f"Introduction Directive content: {self.content}")
        return [nodes.paragraph(text=f"Introduction Directive content: {self.content}")]
    
class ProfessionalExperienceDirective(SphinxDirective):
    has_content = True

    def run(self) -> list[nodes.Node]:
        print(f"Professional Experience Directive content: {self.content}")
        return [nodes.paragraph(text=f"Introduction Directive content: {self.content}")]

def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_directive('introduction', IntroductionDirective)
    app.add_directive('professional_experience', ProfessionalExperienceDirective)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }