import pygame
import discogs_client
import config
import json
import requests
import io

# Initialize Discogs client
d = discogs_client.Client('YourApp/1.0', user_token=config.DISCOGS_USER_TOKEN)

def search_discogs(query, search_type='release'):
    """
    Searches the Discogs database for releases and returns a list of 45rpm releases.
    """
    print(f"\nSearching Discogs for '{query}' (type: {search_type})...")
    release_list = []
    try:
        results = d.search(query, type=search_type)
        if results:
            print(f"Found {results.count} results. Filtering for 45rpm releases.")
            for result in results.page(1):
                if len(release_list) >= 10:
                    break
                if isinstance(result, discogs_client.models.Release):
                    is_45rpm = any(
                        format_entry.get('name') == 'Vinyl' and '7"' in format_entry.get('descriptions', []) and '45 RPM' in format_entry.get('descriptions', [])
                        for format_entry in result.formats or []
                    )
                    if is_45rpm:
                        release_list.append(result)

            if not release_list:
                print("No 45rpm releases found in the first page of results.")
        else:
            print(f"  No {search_type} results found for '{query}'.")
    except Exception as e:
        print(f"An unexpected error occurred during search: {e}")
    return release_list

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.placeholder_text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False
        self.focused = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
                if self.active and self.text == self.placeholder_text:
                    self.text = ''
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return "search"
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
        self.txt_surface = FONT.render(self.text, True, (255,255,255))
        return None

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(screen, self.color if self.active or self.focused else COLOR_INACTIVE, self.rect, 2)

class Button:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.focused = False

    def draw(self, screen):
        color = COLOR_ACTIVE if self.focused else COLOR_INACTIVE
        pygame.draw.rect(screen, color, self.rect)
        search_text = FONT.render(self.text, True, (255, 255, 255))
        screen.blit(search_text, (self.rect.x + 30, self.rect.y + 5))

class Checkbox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.checked = False
        self.focused = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
        if event.type == pygame.KEYDOWN:
            if self.focused and event.key == pygame.K_RETURN:
                self.checked = not self.checked


    def draw(self, screen):
        color = COLOR_ACTIVE if self.focused else COLOR_INACTIVE
        pygame.draw.rect(screen, color, self.rect, 2)
        if self.checked:
            pygame.draw.line(screen, (255, 255, 255), (self.rect.x + 3, self.rect.y + 3), (self.rect.x + self.rect.w - 3, self.rect.y + self.rect.h - 3), 2)
            pygame.draw.line(screen, (255, 255, 255), (self.rect.x + self.rect.w - 3, self.rect.y + 3), (self.rect.x + 3, self.rect.y + self.rect.h - 3), 2)

class ResultsViewer:
    def __init__(self, screen, results):
        self.screen = screen
        self.results = results
        self.font = pygame.font.Font(None, 24)
        self.back_button = Button(10, 10, 100, 32, "Back")
        self.checkboxes = []
        y_offset = 50
        for i, result in enumerate(self.results):
            self.checkboxes.append(Checkbox(50, y_offset, 20, 20))
            y_offset += 60
        self.focused_index = 0
        if self.checkboxes:
            self.checkboxes[self.focused_index].focused = True

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.checkboxes[self.focused_index].focused = False
                self.focused_index = (self.focused_index + 1) % len(self.checkboxes)
                self.checkboxes[self.focused_index].focused = True
            elif event.key == pygame.K_RETURN:
                 if self.checkboxes:
                    self.checkboxes[self.focused_index].handle_event(event)

        for cb in self.checkboxes:
            cb.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back_button.rect.collidepoint(event.pos):
                return "back"
        return None

    def draw(self):
        if not self.results:
            text_surface = self.font.render("No results found.", True, (255, 255, 255))
            self.screen.blit(text_surface, (50, 50))
        else:
            y_offset = 50
            for i, result in enumerate(self.results):
                self.checkboxes[i].draw(self.screen)
                title_surface = self.font.render(f"Title: {result.title}", True, (255, 255, 255))
                artist_surface = self.font.render(f"Artist: {result.artists[0].name if result.artists else 'N/A'}", True, (255, 255, 255))
                year_surface = self.font.render(f"Year: {result.year if result.year else 'N/A'}", True, (255, 255, 255))
                self.screen.blit(title_surface, (80, y_offset))
                self.screen.blit(artist_surface, (80, y_offset + 20))
                y_offset += 60

        self.back_button.draw(self.screen)


def main():
    global FONT, COLOR_INACTIVE, COLOR_ACTIVE
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    FONT = pygame.font.Font(None, 32)
    COLOR_INACTIVE = pygame.Color('lightskyblue3')
    COLOR_ACTIVE = pygame.Color('dodgerblue2')
    pygame.display.set_caption("Music File Cleaner")

    artist_box = InputBox(100, 100, 140, 32, 'Artist')
    title_box = InputBox(100, 200, 140, 32, 'Title')
    search_button = Button(100, 300, 140, 32, 'Search')
    
    focusable_widgets = [artist_box, title_box, search_button]
    focused_widget_index = 0
    focusable_widgets[focused_widget_index].focused = True
    artist_box.active = True


    results_viewer = None
    app_state = "input"

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                if app_state == "input":
                    if event.key == pygame.K_TAB:
                        focusable_widgets[focused_widget_index].focused = False
                        focusable_widgets[focused_widget_index].active = False
                        focused_widget_index = (focused_widget_index + 1) % len(focusable_widgets)
                        focusable_widgets[focused_widget_index].focused = True
                        if isinstance(focusable_widgets[focused_widget_index], InputBox):
                            focusable_widgets[focused_widget_index].active = True
                    elif event.key == pygame.K_RETURN:
                        if focusable_widgets[focused_widget_index] == search_button:
                            search_query = f"{artist_box.text} - {title_box.text}"
                            results = search_discogs(search_query)
                            results_viewer = ResultsViewer(screen, results)
                            app_state = "results"

            if app_state == "input":
                for box in focusable_widgets[:2]:
                    box.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if search_button.rect.collidepoint(event.pos):
                        search_query = f"{artist_box.text} - {title_box.text}"
                        results = search_discogs(search_query)
                        results_viewer = ResultsViewer(screen, results)
                        app_state = "results"
            elif app_state == "results":
                if results_viewer:
                    action = results_viewer.handle_event(event)
                    if action == "back":
                        app_state = "input"

        screen.fill((30, 30, 30))

        if app_state == "input":
            for widget in focusable_widgets:
                widget.draw(screen)
        elif app_state == "results":
            if results_viewer:
                results_viewer.draw()

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()