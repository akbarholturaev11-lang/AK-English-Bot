# -*- coding: utf-8 -*-
"""English lesson generator — assembles full lesson JSON (schema_version 2)
   identical in shape to hsk1/lesson_11.json from a compact spec."""
import json, sys

def T(u,r,j): return {"uz":u,"ru":r,"tj":j}

def build(spec):
    W = spec["words"]          # list of dicts: zh,pinyin,pos,meaning(uz,ru,tj)
    # attach no
    for i,w in enumerate(W,1): w["no"]=i
    def other_meanings(idx,n=3):
        outs=[W[j]["meaning"] for j in range(len(W)) if j!=idx][:n]
        return outs
    def other_words(idx,n=3):
        return [W[j]["zh"] for j in range(len(W)) if j!=idx][:n]
    def other_pins(idx,n=3):
        return [W[j]["pinyin"] for j in range(len(W)) if j!=idx][:n]

    # ---- Section 1: vocab ----
    s1=[]
    pattern=["aw","aw","mg","aw","aw","hc","aw","aw","pc","mp"]
    awi=0; 
    for p in pattern:
        if p=="aw":
            s1.append({"type":"active_word","word":W[awi]}); awi+=1
        elif p=="mg":
            i=0
            s1.append({"type":"meaning_guess",
                "prompt":T(f"«{W[i]['zh']}» ma'nosini tanlang:",f"Выберите значение «{W[i]['zh']}»:",f"Маънои «{W[i]['zh']}»-ро интихоб кунед:"),
                "title":T("Ma'nosi nima?","Что означает?","Маъно чист?"),
                "options":[W[i]["meaning"]]+other_meanings(i),"correct_index":0})
        elif p=="hc":
            i=4
            s1.append({"type":"hanzi_choice",
                "prompt":T(f"«{W[i]['pinyin']}» qaysi so'z?",f"Какое слово читается «{W[i]['pinyin']}»?",f"«{W[i]['pinyin']}» кадом калима аст?"),
                "title":T("So'zni tanlang","Выберите слово","Калимаро интихоб кунед"),
                "options":[W[i]["zh"]]+other_words(i),"correct_index":0})
        elif p=="pc":
            i=0
            s1.append({"type":"pinyin_choice",
                "prompt":T(f"«{W[i]['zh']}» talaffuzini tanlang:",f"Выберите произношение «{W[i]['zh']}»:",f"Талаффузи «{W[i]['zh']}»-ро интихоб кунед:"),
                "title":T("Qanday o'qiladi?","Как читается?","Чӣ хел хонда мешавад?"),
                "options":[W[i]["pinyin"]]+other_pins(i),"correct_index":0})
        elif p=="mp":
            s1.append({"type":"match_pairs","pairs":[[W[k]["zh"],W[k]["meaning"]] for k in range(4)]})

    # ---- Section 2: grammar ----
    G=spec["grammar"]
    s2=[{"type":"_grammar","g":dict(no=i+1,**G[i])} for i in range(len(G))]
    s2.append(dict(type="sentence_builder",**spec["sentence_builder"]))
    qz=spec["quick_quiz_1"]
    s2.append({"type":"quick_quiz","prompt":qz["prompt"],"title":T("To'g'ri javobni tanlang","Выберите правильный ответ","Ҷавоби дурустро интихоб кунед"),"options":qz["options"],"correct_index":qz["correct_index"]})

    # ---- Section 3: practice ----
    i2=1
    s3=[
      {"type":"pinyin_choice",
        "prompt":T(f"«{W[i2]['zh']}» talaffuzini tanlang:",f"Выберите произношение «{W[i2]['zh']}»:",f"Талаффузи «{W[i2]['zh']}»-ро интихоб кунед:"),
        "title":T("Qanday o'qiladi?","Как читается?","Чӣ хел хонда мешавад?"),
        "options":[W[i2]["pinyin"]]+other_pins(i2),"correct_index":0},
      {"type":"meaning_guess",
        "prompt":T(f"«{W[5]['zh']}» ma'nosini tanlang:",f"Выберите значение «{W[5]['zh']}»:",f"Маънои «{W[5]['zh']}»-ро интихоб кунед:"),
        "title":T("Ma'nosi nima?","Что означает?","Маъно чист?"),
        "options":[W[5]["meaning"]]+other_meanings(5),"correct_index":0},
      dict(type="listening_choice",**spec["listening_1"]),
      {"type":"match_pairs","pairs":[[W[k]["zh"],W[k]["meaning"]] for k in range(4,8)]},
      dict(type="pronunciation",**spec["pronunciation_1"]),
    ]

    # ---- Section 4: dialog ----
    s4=[
      dict(type="listening_choice",**spec["listening_2"]),
      dict(type="gap_fill",**spec["gap_fill_1"]),
      dict(type="dialog_cloze",**spec["dialog_cloze_1"]),
    ]
    qz2=spec["quick_quiz_2"]
    s4.append({"type":"quick_quiz","prompt":qz2["prompt"],"title":T("To'g'ri javobni tanlang","Выберите правильный ответ","Ҷавоби дурустро интихоб кунед"),"options":qz2["options"],"correct_index":qz2["correct_index"]})

    lesson={
      "schema_version":2,"level":spec["level"],"lesson_id":spec["lesson_id"],
      "title":spec["title"],"subtitle":spec["subtitle"],
      "intro_prebuilt":True,"grammar_prebuilt":True,
      "active_words":W,
      "grammar":[dict(no=i+1,**G[i]) for i in range(len(G))],
      "dialogues":spec["dialogues"],
      "sections":[
        {"section_no":1,"section_title":T("Yangi so'zlar","Новые слова","Калимаҳои нав"),"cards":s1},
        {"section_no":2,"section_title":T("Grammatika","Грамматика","Грамматика"),"cards":s2},
        {"section_no":3,"section_title":T("Mashq","Практика","Машқ"),"cards":s3},
        {"section_no":4,"section_title":T("Dialog","Диалог","Муколама"),"cards":s4},
      ]
    }
    return lesson

if __name__=="__main__":
    import importlib.util
    specmod=sys.argv[1]
    spec=json.load(open(specmod,encoding="utf-8"))
    out=build(spec)
    path=f"{spec['level']}/lesson_{spec['lesson_id']:02d}.json"
    json.dump(out,open(path,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print("wrote",path,"| cards:",[len(s["cards"]) for s in out["sections"]])
