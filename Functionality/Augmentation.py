from AiOrchestration.AiOrchestrator import AiOrchestrator


class Augmentation:

    @staticmethod
    def augment_prompt(initial_prompt: str):
        executor = AiOrchestrator()

        # ToDo: Indepth study of prompt engineering principles and testing to optimise this prompt
        result = executor.execute(
            ["""Take the given user prompt and rewrite it augmenting it in line with prompt engineering standards. 
            Increase clarity, state facts simply, use for step by step reasoning. 
            Returning *only* the new and improved user prompt
            Augment user prompt with as many prompt engineering standards crammed in as possible, don't answer it"""],
            ["user prompt: \"\"\"\n" + initial_prompt + "\n\"\"\""]
        )

        return result

    @staticmethod
    def question_user_prompt(initial_prompt: str):
        executor = AiOrchestrator()

        # ToDo: Indepth study of what makes for the best questions (after graph database has been developed)
        result = executor.execute(
            ["""Given the following user prompt what are your questions, be concise and targeted. 
            Just ask the questions you wpi;d like to know before answering my prompt, do not actually answer my prompt"""],
            [initial_prompt]
        )

        return result


if __name__ == '__main__':
    Augmentation.augment_prompt("Whats the best way to go from paris to london?")
    # Augmentation.augment_prompt("Can you recommend me a good tech stack for my chatGpt wrapper application?")