.PHONY: all build run clean install uninstall debug release

# Compiler ve Flags
COMPILER = clang++
FLAGS = -std=c++11 -Wall -Wextra
DEBUG_FLAGS = -g -O0
RELEASE_FLAGS = -O2 -DNDEBUG

# Target
TARGET = m3sfmode
SRC = src/main.cpp
OBJ = $(SRC:.cpp=.o)

# Build Directory
BUILD_DIR = build
DEBUG_DIR = $(BUILD_DIR)/debug
RELEASE_DIR = $(BUILD_DIR)/release

# Platform Detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    PLATFORM = Linux
endif
ifeq ($(UNAME_S),Darwin)
    PLATFORM = macOS
    COMPILER = clang++
endif
ifdef WINDOWSDIR
    PLATFORM = Windows
endif

# Varsayılan hedef
all: release

# Debug Build
debug: COMPILER_FLAGS = $(FLAGS) $(DEBUG_FLAGS)
debug: $(DEBUG_DIR)/$(TARGET)
	@echo "✓ Debug build tamamlandı!"

$(DEBUG_DIR)/$(TARGET): $(DEBUG_DIR)/main.o
	@mkdir -p $(DEBUG_DIR)
	$(COMPILER) $(COMPILER_FLAGS) -o $@ $^
	@echo "[DEBUG BUILD] $@"

$(DEBUG_DIR)/main.o: $(SRC)
	@mkdir -p $(DEBUG_DIR)
	$(COMPILER) $(COMPILER_FLAGS) -c $< -o $@

# Release Build (Varsayılan)
release: COMPILER_FLAGS = $(FLAGS) $(RELEASE_FLAGS)
release: $(RELEASE_DIR)/$(TARGET)
	@echo "✓ Release build tamamlandı!"

$(RELEASE_DIR)/$(TARGET): $(RELEASE_DIR)/main.o
	@mkdir -p $(RELEASE_DIR)
	$(COMPILER) $(COMPILER_FLAGS) -o $@ $^
	@echo "[RELEASE BUILD] $@"

$(RELEASE_DIR)/main.o: $(SRC)
	@mkdir -p $(RELEASE_DIR)
	$(COMPILER) $(COMPILER_FLAGS) -c $< -o $@

# Çalıştır (Derleme + Çalışma)
run: release
	@echo ""
	@echo "════════════════════════════════════════"
	@echo "  M3SFMODE - Başlatılıyor..."
	@echo "════════════════════════════════════════"
	@echo ""
	@$(RELEASE_DIR)/$(TARGET)

# Direkten çalıştır (derleme olmadan)
run-debug: debug
	@echo ""
	@echo "════════════════════════════════════════"
	@echo "  M3SFMODE - Debug Mod"
	@echo "════════════════════════════════════════"
	@echo ""
	@$(DEBUG_DIR)/$(TARGET)

# Temizle
clean:
	@echo "[CLEANING] Eski dosyalar siliniyor..."
	@rm -rf $(BUILD_DIR)
	@rm -f $(TARGET)
	@rm -f *.o
	@echo "✓ Temizlik tamamlandı!"

# İnstall (Linux/macOS)
install: release
	@echo "[INSTALL] M3SFMODE sistem'e kuruluyor..."
	@sudo cp $(RELEASE_DIR)/$(TARGET) /usr/local/bin/
	@sudo chmod +x /usr/local/bin/$(TARGET)
	@echo "✓ Kurulum tamamlandı!"
	@echo "  Kullanım: m3sfmode"

# Uninstall
uninstall:
	@echo "[UNINSTALL] M3SFMODE kaldırılıyor..."
	@sudo rm -f /usr/local/bin/$(TARGET)
	@echo "✓ Kaldırma tamamlandı!"

# Info
info:
	@echo "════════════════════════════════════════"
	@echo "  M3SFMODE Build System"
	@echo "════════════════════════════════════════"
	@echo "  Platform: $(PLATFORM)"
	@echo "  Compiler: $(COMPILER)"
	@echo "  Source: $(SRC)"
	@echo "  Target: $(TARGET)"
	@echo ""
	@echo "Komutlar:"
	@echo "  make              - Release derle"
	@echo "  make debug        - Debug derle"
	@echo "  make run          - Derle ve çalıştır"
	@echo "  make run-debug    - Debug derle ve çalıştır"
	@echo "  make clean        - Eski dosyaları sil"
	@echo "  make install      - Sistem'e kur"
	@echo "  make uninstall    - Sistem'den kaldır"
	@echo "  make info         - Bu bilgiyi göster"
	@echo "════════════════════════════════════════"

# Help
help: info

.PHONY: help info
