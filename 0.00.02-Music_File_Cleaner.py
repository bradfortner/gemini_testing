import pygame
import discogs_client
import config

# Initialize Discogs client
# The user token is now imported from config.py
d = discogs_client.Client('YourApp/1.0', user_token=config.DISCOGS_USER_TOKEN)

def search_discogs(query, search_type='release'):
    """
    Searches the Discogs database for releases, artists, or masters.
    """
    print(f"\nSearching Discogs for '{query}' (type: {search_type})...")
    try:
        results = d.search(query, type=search_type)
        if results:
            print(f"Found {results.count} results. Showing the first 5:")
            for i, result in enumerate(results.page(1)):
                if i >= 5:
                    break
                print(f"  Result {i+1}:")
                if isinstance(result, discogs_client.models.Release):
                    print(f"    Title: {result.title}")
                    print(f"    Artist: {result.artists[0].name if result.artists else 'N/A'}")
                    print(f"    Year: {result.year}")
                    print(f"    Labels: {', '.join([l.name for l in result.labels])}")
                elif isinstance(result, discogs_client.models.Artist):
                    print(f"    Name: {result.name}")
                elif isinstance(result, discogs_client.models.Master):
                    print(f"    Title: {result.title}")
                    print(f"    Artist: {result.artists[0].name if result.artists else 'N/A'}")
                    print(f"    Year: {result.year}")
        else:
            print(f"  No {search_type} results found for '{query}'.")
    except Exception as e:
        print(f"Error searching Discogs: {e}")


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, (255, 255, 255))

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)


def main():
    global FONT, COLOR_INACTIVE, COLOR_ACTIVE
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    FONT = pygame.font.Font(None, 32)
    COLOR_INACTIVE = pygame.Color('lightskyblue3')
    COLOR_ACTIVE = pygame.Color('dodgerblue2')
    pygame.display.set_caption("Music File Cleaner")

    artist_box = InputBox(100, 100, 140, 32, 'Artist')
    title_box = InputBox(100, 200, 140, 32, 'Title')
    input_boxes = [artist_box, title_box]
    
    search_button = pygame.Rect(100, 300, 140, 32)

    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            for box in input_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if search_button.collidepoint(event.pos):
                    search_query = f"{artist_box.text} - {title_box.text}"
                    search_discogs(search_query)


        screen.fill((30, 30, 30))
        for box in input_boxes:
            box.draw(screen)

        pygame.draw.rect(screen, COLOR_INACTIVE, search_button)
        search_text = FONT.render("Search", True, (255, 255, 255))
        screen.blit(search_text, (search_button.x + 30, search_button.y + 5))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
