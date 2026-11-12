from config import Config
from screen import convert_screen_to_monitor, grab
from utils.custom_mouse import mouse
from utils.misc import cut_roi, wait
from logger import Logger
from config import Config
from d2r_image import ocr

def get_experience():
    # mouseover exp bar
    pos=(Config().ui_pos["xp_bar_x"], Config().ui_pos["xp_bar_y"])
    x_m, y_m =  convert_screen_to_monitor(screen_coord = pos)
    mouse.move(x_m, y_m, randomize = (8,1))
    wait(0.05)
    # crop roi
    img = grab()

    mouse.move(x_m, y_m-50, randomize = (8,1))
    crop = cut_roi(img, Config().ui_roi["xp_bar_text"])
    ocr_result = ocr.image_to_text(
        images = crop,
        model = "ground-eng_inconsolata_inv_th_fast",
        psm = 7,
        scale = 1.3,
        crop_pad = True,
        erode = True,
        invert = True,
        digits_only = False,
        fix_regexps = False,
        check_known_errors = False,
        correct_words = False
    )[0]

    split_text = ocr_result.text.split(' ')
    Logger.info(f"ocr experience: {split_text}")
    
    try:
        # Search for "EXP" to get the correct starting point
        index = next((i for i, s in enumerate(split_text) if "EXP" in s), None)
        
        # Use 'is not None' because index 0 is a valid position!
        if index is not None:
            # Ensure the list is long enough to have indices [index+1] and [index+3]
            if len(split_text) > index + 3:
                # Cleaning and converting
                curr_raw = split_text[index + 1].replace(',', '').replace('.', '')
                req_raw = split_text[index + 3].replace(',', '').replace('.', '')
                
                # Using digit filter for maximum safety against stray OCR characters
                current_exp = int(''.join(filter(str.isdigit, curr_raw)))
                required_exp = int(''.join(filter(str.isdigit, req_raw)))
                
                return current_exp, required_exp
            else:
                Logger.warning(f"Found 'EXP' but data is missing or incomplete: {split_text}")
        
        else:
            Logger.warning(f"Can not find 'EXP' in OCR text: {split_text}.")
            
        return 0, 0
        
    except Exception as e:
        Logger.warning(f"EXP OCR Error: {split_text}. Exception: {e}")
        return 0, 0


if __name__ == "__main__":
    import keyboard
    import os

    from screen import start_detecting_window
    start_detecting_window()

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    print("Go to D2R window and press f11 to start game")
    keyboard.wait("f11")

    exp = get_experience()
    Logger.debug(f"EXP curr: {exp[0]}")
    Logger.debug(f"EXP req: {exp[1]}")
    Logger.debug(f"EXP per: {exp[2]}")
