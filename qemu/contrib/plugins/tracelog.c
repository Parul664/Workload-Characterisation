/*
 * This plugin is a combination of the insn plugin present in tests/plugin and execlog plugin present in contrib/plugins.
 */
#include <glib.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>

#include <qemu-plugin.h>

QEMU_PLUGIN_EXPORT int qemu_plugin_version = QEMU_PLUGIN_VERSION;

/* Store last executed instruction on each vCPU as a GString */
GArray *last_exec;
static uint64_t insn_count;
static uint64_t start_pnt; 
static uint64_t trace_count;
static int start_tracing;
static uint64_t nop_count;
static int MILLION = 0;
static FILE *filePtr;
/**
 * Log instruction execution
 */
static void vcpu_insn_exec(unsigned int cpu_index, void *udata)
{

    if(!start_tracing)
        return;

    if (insn_count >= start_pnt && insn_count < start_pnt + trace_count){
        GString *s;

        /* Find or create vCPU in array */
        while (cpu_index >= last_exec->len) {
            s = g_string_new(NULL);
            g_array_append_val(last_exec, s);
        }
        s = g_array_index(last_exec, GString *, cpu_index);

        /* Print previous instruction in cache */
        // if (s->len) {
        //     qemu_plugin_outs(s->str);
        //     qemu_plugin_outs("\n");
        // }
        if(s->len){
            fprintf(filePtr, "%s\n", s->str);
        }

        /* Store new instruction in cache */
        /* vcpu_mem will add memory access information to last_exec */
        g_string_printf(s, "%u, ", cpu_index);
        // new addtion by me
        if(MILLION==1000000){
            //g_string_printf(s, " <insCount -> %ld>, <nopCount -> %ld>  ", insn_count, nop_count);
            MILLION = 0;
        }
        g_string_append(s, (char *)udata);
    
    }else{
        fprintf(filePtr, "%ld\n", insn_count);
    }
    MILLION++;
    insn_count++;
}

/**
 * On translation block new translation
 *
 * QEMU convert code by translation block (TB). By hooking here we can then hook
 * a callback on each instruction and memory access.
 */
static void vcpu_tb_trans(qemu_plugin_id_t id, struct qemu_plugin_tb *tb)
{
    struct qemu_plugin_insn *insn;
    uint64_t insn_vaddr;
    uint32_t insn_opcode;
    char *insn_disas;

    size_t n = qemu_plugin_tb_n_insns(tb);
    for (size_t i = 0; i < n; i++) {
        /*
         * `insn` is shared between translations in QEMU, copy needed data here.
         * `output` is never freed as it might be used multiple times during
         * the emulation lifetime.
         * We only consider the first 32 bits of the instruction, this may be
         * a limitation for CISC architectures.
         */
        insn = qemu_plugin_tb_get_insn(tb, i);
        insn_vaddr = qemu_plugin_insn_vaddr(insn);
        insn_opcode = *((uint32_t *)qemu_plugin_insn_data(insn));
        insn_disas = qemu_plugin_insn_disas(insn);

        if(strstr(insn_disas, "nop")){
            nop_count += 1;
            //printf("%ld\n", nop_count);
            // printf("increasing nop count %ld\n", nop_count);
        }else{
            nop_count = 0;
        }

        
        
        char *output = g_strdup_printf("0x%"PRIx64", 0x%"PRIx32", \"%s\", 0x%"PRIx64"",
                                       insn_vaddr, insn_opcode, insn_disas, nop_count);

        // if(insn_vaddr > 0x80000000){
        //     output = "";
        // }
        if(nop_count == 997){
            start_tracing = (start_tracing == 1) ? 0 : 1;
            //printf("Start tracing set to 1");
        }
        qemu_plugin_register_vcpu_insn_exec_cb(insn, vcpu_insn_exec,
                                               QEMU_PLUGIN_CB_NO_REGS, output);
    }
    
}

/**
 * On plugin exit, print last instruction in cache
 */
static void plugin_exit(qemu_plugin_id_t id, void *p)
{
    guint i;
    GString *s;
    for (i = 0; i < last_exec->len; i++) {
        s = g_array_index(last_exec, GString *, i);
        if (s->str) {
            qemu_plugin_outs(s->str);
            qemu_plugin_outs("\n");
        }
    }
    g_autofree gchar *out;
    out = g_strdup_printf("insns: %" PRIu64 "\n", insn_count);
    qemu_plugin_outs(out);
    fclose(filePtr);
}


static void plugin_init(void)
{
    start_tracing = 0;
    nop_count = 0;
    filePtr = fopen("instTrace.log", "w");
    last_exec = g_array_new(FALSE, FALSE, sizeof(GString *));
}

/**
 * Install the plugin
 */
QEMU_PLUGIN_EXPORT int qemu_plugin_install(qemu_plugin_id_t id,
                                           const qemu_info_t *info, int argc,
                                           char **argv)
{
    // signal(40, sig_handler);
    
    start_pnt = 0; 
    trace_count = __LONG_LONG_MAX__;
    for (int i = 0; i < argc; i++) {
        char *p = argv[i];
        g_autofree char **tokens = g_strsplit(p, "=", -1);
        if (g_strcmp0(tokens[0], "start") == 0) {
            printf("%s : %s\n", tokens[0], tokens[1]);
            char *value = tokens[1];
            start_pnt = strtoull(value, NULL, 0);

        } else if (g_strcmp0(tokens[0], "count") == 0) {
            printf("%s : %s\n", tokens[0], tokens[1]);
            char *value = tokens[1];
            trace_count = strtoull(value, NULL, 0);
        } else {
            fprintf(stderr, "option parsing failed: %s\n", p);
            return -1;
        }
    }
    
    plugin_init();

    /* Register translation block and exit callbacks */
    qemu_plugin_register_vcpu_tb_trans_cb(id, vcpu_tb_trans);
    qemu_plugin_register_atexit_cb(id, plugin_exit, NULL);

    return 0;
}