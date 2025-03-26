# MILA
MInimizing LLM Prompts in Ontology MApping

## Overview
Ontology matching (OM) plays a key role in enabling data interoperability and knowledge sharing. Recently,
methods based on Large Language Model (LLMs) have shown great promise in OM, particularly through the use of
a retrieve-then-prompt pipeline. In this approach, relevant target entities are first retrieved and then used to prompt
the LLM to predict the final matches. Despite their potential, these systems still present limited performance and
high computational overhead. To address these issues, we introduce MILA, a novel approach that embeds a retrieve-
identify-prompt pipeline within a prioritized depth-first search (PDFS) strategy. This approach efficiently identifies
a large number of semantic correspondences with high accuracy, limiting LLM requests to only the most borderline
cases. We evaluated MILA using three challenges from the 2024 edition of the Ontology Alignment Evaluation
Initiative. Our method achieved the highest F-Measure in five of seven unsupervised tasks, outperforming state-
of-the-art OM systems by up to 17%. It also performed better than or comparable to the leading supervised OM
systems. MILA further exhibited task-agnostic performance, remaining stable across all tasks and settings, while
significantly reducing runtime. These findings highlight that high-performance LLM-based OM can be achieved
through a combination of programmed (PDFS), learned (embedding vectors), and prompting-based heuristics, without
the need of domain-specific heuristics or fine-tuning.
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5074656

# 🔍 MILA: MInimizing LLM Prompts in Ontology MApping 

![MILA Overview](images/Figure_1.jpg) 



## Workflow
MILA consists of **two main steps**:

1️⃣ Vector KB Construction & Mapping Prediction (run file KBs_Building.py)  
   - Inputs: The source and target ontologies  
   - Outputs: Vector KB for each ontology (optional) & correspondence candidates  

2️⃣ The Retrieve-Identify-Prompt Pipeline (run file rip_pipeline.py)  
   - Inputs: dataset of source entities to be mapped & correspondence candidates  
   - Outputs: Final correspondences  


## ⚙️ Configuration

MILA uses a `config.yaml` file to customize parameters, and specify path to load all the data. 
You can modify this file to adjust
1) Ontology-related configurations and directory paths for various data files used in the ontology processing
2) Dataset-related configurations and paths
3) Prompt template-related paths
4) Correspondences-related configurations and paths
5) Configuration for ontology and dataset read methods defined by the user
6) Configuration for LLM access methods defined by the user

📂 Customizable Methods Folder
MILA includes a folder called user_methods where users can define their own functions to:
✅ Read ontologies in different formats (e.g., OWL, RDF, or custom formats).
✅ Query an LLM using different APIs or models.

This folder contains two key files:

✅read_methods.py: Handles ontology file reading.
✅LLM_methods.py: Defines how to interact with an LLM.


---

## 📦 Installation

1️⃣ **Clone the repository**  
```bash
git clone https://github.com/your-username/mila.git
cd mila
