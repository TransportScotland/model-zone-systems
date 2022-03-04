from pathlib import Path
from typing import Optional
from urllib.parse import quote

import geopandas as gpd
import matplotlib.pyplot as plt


def markdown_image_reference(image_path: Path, alt_text: Optional[str]=None, link: Optional[Path]=None):
    """Creates a markdown reference for an image, with optional alt text and link
    """
    image_str = quote(str(image_path))
    alt_str = alt_text or image_path.stem
    link_str = quote(str(link)) if link else image_str

    return f'[![{alt_str}]({image_str})]({link_str})\n\n'


def generate_zone_preview(file_path: Path, model_name: str):
    """Produces a preview of a zone shapefile.
    """
    # Read in the file
    data = gpd.read_file(file_path)

    # Set up axes
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Labels etc
    ax.axis('off')
    ax.set_title(
        f'{model_name}\nZone Overview', 
        va='bottom',
        size='xx-large', weight='bold'
    )
    ax.annotate(
        f'Provided for reference only.\nFor more information visit github.com/transportscotland/model-zone-systems', 
        xy=(0, 0), xycoords='axes fraction', 
        xytext=(0, -10), textcoords='offset pixels', 
        ha='left', size='x-small'
    )

    # Draw it.
    data.plot(ax=ax)

    return fig, ax


if __name__ == '__main__':
    base_folder = Path(__file__).parent

    for obj in (base_folder / 'Zones').iterdir():
        # Loop over folders
        if obj.is_dir():
            # Set up image previews folder
            image_folder = obj / 'Previews'
            image_folder.mkdir(exist_ok=True)

            # Start accumulating text for our readme.md
            preview_text = ''
            for zf in obj.glob('*.zip'):
                model_name = zf.stem
                fig_path = image_folder / f'{model_name}.png'

                # # Draw the image, save it.
                fig, ax = generate_zone_preview(f'zip://{zf.absolute()}', model_name)
                plt.savefig(fig_path, bbox_inches='tight')
                plt.close()

                # Get the image and link ready
                preview_text += markdown_image_reference(
                    fig_path.relative_to(obj), 
                    alt_text=f'{model_name} Preview', 
                    link=zf.relative_to(obj)
                )
                
            # If we've generated any previews, write our readme file.
            if preview_text:
                with (obj / 'README.md').open('w') as readme:
                    readme.write(
                        '# Zone previews\n**AUTOMATICALLY GENERATED, DO NOT MODIFY**\n\n'
                        'Click an image to go directly to the corresponding zip file\n\n'
                        + preview_text
                    )
