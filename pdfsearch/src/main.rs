use lopdf::Document;
use std::env;
use std::fs;
use std::path::Path;

fn main() {
    // Collect command-line arguments
    let args: Vec<String> = env::args().collect();

    if args.len() < 3 {
        eprintln!("Usage: {} <file_or_directory> <word1> [<word2> ...]", args[0]);
        std::process::exit(1);
    }

    // Extract the file or directory path and search words
    let input_path = &args[1];
    let search_words = &args[2..];

    // Check if the input path is a file or directory
    let path = Path::new(input_path);
    if path.is_file() {
        process_file(input_path, search_words);
    } else if path.is_dir() {
        for entry in fs::read_dir(input_path).unwrap_or_else(|err| {
            eprintln!("Failed to read directory '{}': {}", input_path, err);
            std::process::exit(1);
        }) {
            if let Ok(entry) = entry {
                let file_path = entry.path();
                if file_path.is_file() && file_path.extension().map_or(false, |ext| ext == "pdf") {
                    process_file(file_path.to_str().unwrap(), search_words);
                }
            }
        }
    } else {
        eprintln!("The provided path is neither a file nor a directory: {}", input_path);
        std::process::exit(1);
    }
}

fn process_file(file_path: &str, search_words: &[String]) {
    // Load the PDF document
    let pdf = Document::load(file_path).unwrap_or_else(|err| {
        eprintln!("Failed to load PDF file '{}': {}", file_path, err);
        return;
    });

    // Iterate through the pages and search for words
    for (page_number, page_id) in pdf.get_pages() {
        if let Ok(page_content) = pdf.extract_text(&[page_id]) {
            for word in search_words {
                if page_content.contains(word) {
                    println!("Found '{}' in file '{}' on page {}", word, file_path, page_number);
                }
            }
        }
    }
}
