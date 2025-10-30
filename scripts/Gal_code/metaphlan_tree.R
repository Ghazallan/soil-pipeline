# =============================
# 1. Load packages
# =============================
library(tidyverse)
library(ape)
library(ggtree)
library(ggtreeExtra)
library(data.tree)
library(purrr)
library(stringr)

# =============================
# 2. Read MetaPhlAn output
# =============================
meta_file <- "C:/Users/hadis/OneDrive/Documents/Project/MetaPhlAn_on_data_1__Predicted_taxon_relative_abundances_SCBI_012.tabular"


meta <- read_tsv(meta_file, skip = header_line - 1, show_col_types = FALSE)
cat("✅ File read successfully\n")
print(head(meta))

# =============================
# 3. Clean & prepare taxonomy
# =============================
meta_clean <- meta %>%
  select(`#clade_name`, NCBI_tax_id, abundance = relative_abundance) %>%
  rename(clade_name = `#clade_name`) %>%
  filter(!is.na(abundance), abundance > 0)




cat("✅ Cleaned taxonomy:\n")
print(head(meta_clean))

# Dynamically detect depth
n_levels <- max(str_count(meta_clean$clade_name, "\\|")) + 1

meta_long <- meta_clean %>%
  separate(clade_name, into = paste0("level", 1:n_levels), sep = "\\|", fill = "right") %>%
  mutate(label = coalesce(!!!syms(paste0("level", n_levels:1))))

# =============================
# 4. Build taxonomy tree
# =============================
edges <- meta_long %>%
  mutate(path = pmap_chr(select(., starts_with("level")),
                         ~ paste(na.omit(c(...)), collapse = "/"))) %>%
  distinct(path, .keep_all = TRUE)

tax_tree <- as.Node(edges, pathName = "path")
nwk <- ToNewick(tax_tree, drop.internal = FALSE)
tree <- read.tree(text = nwk)
cat("✅ Tree built successfully\n")

# =============================
# 5. Add abundance
# =============================
abund_data <- meta_long %>%
  group_by(label) %>%
  summarise(abundance = sum(abundance), .groups = "drop")

# =============================
# 6. Plot circular dendrogram
# =============================
p <- ggtree(tree, layout = "circular", size = 0.3)
p <- p %<+% abund_data +
  geom_tippoint(aes(size = abundance, color = abundance)) +
  scale_size_continuous(range = c(0.5, 6)) +
  scale_color_viridis_c(option = "plasma") +
  theme_void() +
  ggtitle("MetaPhlAn Taxonomic Circular Dendrogram") +
  theme(legend.position = "right",
        plot.title = element_text(hjust = 0.5, face = "bold"))

print(p)
cat("✅ Plot generated successfully\n")
# =============================
# End of script